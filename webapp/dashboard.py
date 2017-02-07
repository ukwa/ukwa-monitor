
import io
import os
import json
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


@app.route('/')
def status():

    # Attempt to load current statistics, if available:
    for mins in range(0,30):
        try:
            json_file = CheckStatus(date=datetime.datetime.today()-datetime.timedelta(minutes=mins)).output().path
            #json_file = "../state/monitor/checkstatus.2016-11-22T1110"
            services = load_services(json_file)
        except Exception as e:
            app.logger.info("Could not load %i mins ago..." % mins)

    # Log collected data:
    #app.logger.info(json.dumps(services, indent=4))

    # And render
    return render_template('dashboard.html', title="Status", services=services)


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
    (warc_filename, warc_offset) = lookup_in_cdx(qurl)

    # If not found, say so:
    if warc_filename is None:
        abort(404)

    # Grab the payload from the WARC and return it.
    WEBHDFS_PREFIX = os.environ['WEBHDFS_PREFIX']
    HDFS_PREFIX = os.environ['HDFS_PREFIX']
    r = requests.get("%s%s%s?op=OPEN&user.name=%s&offset=%s" % (WEBHDFS_PREFIX, HDFS_PREFIX,
                                                           warc_filename, webhdfs().user, warc_offset))
    app.logger.info("Loading from: %s" % r.url)
    r.raw.decode_content = False
    rl = ArcWarcRecordLoader()
    record = rl.parse_record_stream(DecompressingBufferedReader(stream=io.BytesIO(r.content)))
    print(record)
    print(record.length)
    print(record.stream.limit)

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
                return file, compressedoffset
        except Exception as e:
            app.logger.error("Lookup failed for %s!" % qurl)
            app.logger.exception(e)
        #for de in dom.getElementsByTagName('capturedate'):
        #    if de.firstChild.nodeValue == self.ts:
        #        # Excellent, it's been found:
        #        return
    return None, None


if __name__ == "__main__":
    os.environ['CDX_SERVER'] = "http://localhost:9090/fc"
    os.environ['WEBHDFS_PREFIX'] = "http://localhost:50070/webhdfs/v1"
    os.environ['HDFS_PREFIX'] = "/1_data/pulse"
    os.environ['LUIGI_STATE_FOLDER'] = ".."
    app.run(debug=True, port=5505, use_reloader=False)
