
import io
import os
import json
import logging
import datetime
from requests.utils import quote
import xml.dom.minidom
import requests
from pywb.warc.recordloader import ArcWarcRecordLoader
from pywb.utils.bufferedreaders import DecompressingBufferedReader
from tasks.monitor import CheckStatus
from luigi.contrib.hdfs.webhdfs_client import webhdfs
from flask import Flask
from flask import render_template, redirect, url_for, request, Response, send_file, abort
app = Flask(__name__)

@app.before_first_request
def setup_logging():
    if not app.debug:
        # In production mode, add log handler to sys.stderr.
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)

@app.route('/')
def status():

    # Get services and status:
    services = load_service_status()

    # Log collected data:
    #app.logger.info(json.dumps(services, indent=4))

    # And render
    return render_template('dashboard.html', title="Status", services=services)


@app.route('/overview')
def overview():

    app.logger.info(os.environ)

    # Get services and status:
    services = load_service_status()

    # Set up colour mappings:
    colours = {}
    colours["status-alert"] = '#E73F3F'
    colours['status-warning'] = '#F76C27'
    colours['status-okay'] = '#E7E737'
    colours['status-in-flux'] = '#6D9DD1'
    colours['status-oos'] = '#6D9DD1'
    colours['status-good'] = 'rgb(28, 184, 65)'
    colours['status-unknown'] = "red"

    # Log collected data:
    # app.logger.info(json.dumps(services, indent=4))

    # And render
    return render_template('overview.html', title="Overview", services=services, colours=colours)


def load_service_status():
    services = None
    # Attempt to load current statistics, backtracking until stats are available:
    for mins in range(0,60):
        try:
            status_date = datetime.datetime.today() - datetime.timedelta(minutes=mins)
            json_file = CheckStatus(date=status_date).output().path
            #json_file = "../state/monitor/checkstatus.2016-11-22T1110"
            services = load_services(json_file)
            services['status_date'] = status_date.isoformat()
            services['status_date_delta'] = mins
            if( mins > 2 ):
                services['status_date_warning'] = "Status data is %s minutes old!" % mins
        except Exception as e:
            app.logger.info("Could not load %i mins ago... %s" % (mins, e))
            #app.logger.exception(e)

        if services is not None:
            break

    if services is None:
        abort(500, "Could not load a recent service status file!")

    return services

def load_services(json_file):
    app.logger.info("Attempting to load %s" % json_file)
    with open(json_file, 'r') as reader:
        services = json.load(reader)
    return services


@app.route('/ping')
def ping_pong():
    return 'pong!'


@app.route('/get-rendered-original')
def get_rendered_original():
    """
    Grabs a rendered resource.

    Only reason Wayback can't do this is that it does not like the extended URIs
    i.e. 'screenshot:http://' and replaces them with 'http://screenshot:http://'
    """
    url = request.args.get('url')
    app.logger.debug("Got URL: %s" % url)
    #
    type = request.args.get('type', 'screenshot')
    app.logger.debug("Got type: %s" % type)

    # Query URL
    qurl = "%s:%s" % (type, url)
    # Query CDX Server for the item
    app.logger.info("Querying CDX for prefix...")
    warc_filename, warc_offset, compressedendoffset = lookup_in_cdx(qurl)

    # If not found, say so:
    if warc_filename is None:
        abort(404)

    # Grab the payload from the WARC and return it.
    WEBHDFS_PREFIX = os.environ['WEBHDFS_PREFIX']
    url = "%s%s?op=OPEN&user.name=%s&offset=%s" % (WEBHDFS_PREFIX, warc_filename, webhdfs().user, warc_offset)
    if compressedendoffset:
        url = "%s&length=%s" % (url, compressedendoffset)
    app.logger.info("Requesting copy from HDFS: %s " % url)
    r = requests.get(url, stream=True)
    app.logger.info("Loading from: %s" % r.url)
    r.raw.decode_content = False
    rl = ArcWarcRecordLoader()
    app.logger.info("Passing response to parser...")
    record = rl.parse_record_stream(DecompressingBufferedReader(stream=r.raw))
    app.logger.info("RESULT:")
    app.logger.info(record)

    app.logger.info("Returning stream...")
    return send_file(record.stream, mimetype=record.content_type)

    #return "Test %s@%s" % (warc_filename, warc_offset)


def lookup_in_cdx(qurl):
    """
    Checks if a resource is in the CDX index.
    :return:
    """
    CDX_SERVER = os.environ['CDX_SERVER']
    query = "%s?q=type:urlquery+url:%s" % (CDX_SERVER, quote(qurl))
    r = requests.get(query)
    print(r.url)
    app.logger.debug("Availability response: %d" % r.status_code)
    print(r.status_code, r.text)
    # Is it known, with a matching timestamp?
    if r.status_code == 200:
        try:
            dom = xml.dom.minidom.parseString(r.text)
            for result in dom.getElementsByTagName('result'):
                file = result.getElementsByTagName('file')[0].firstChild.nodeValue
                compressedoffset = result.getElementsByTagName('compressedoffset')[0].firstChild.nodeValue
                # Support compressed record length if present:
                if( len(result.getElementsByTagName('compressedendoffset')) > 0):
                    compressedendoffset = result.getElementsByTagName('compressedendoffset')[0].firstChild.nodeValue
                else:
                    compressedendoffset = None
                return file, compressedoffset, compressedendoffset
        except Exception as e:
            app.logger.error("Lookup failed for %s!" % qurl)
            app.logger.exception(e)
        #for de in dom.getElementsByTagName('capturedate'):
        #    if de.firstChild.nodeValue == self.ts:
        #        # Excellent, it's been found:
        #        return
    return None, None, None


if __name__ == "__main__":
    os.environ['CDX_SERVER'] = "http://localhost:9090/fc"
    os.environ['WEBHDFS_PREFIX'] = "http://localhost:50070/webhdfs/v1"
    os.environ['HDFS_PREFIX'] = "/1_data/pulse"
    os.environ['LUIGI_STATE_FOLDER'] = "/var/log/luigi/task-state/"
    app.run(debug=True, port=5000, host="0.0.0.0", use_reloader=False)
