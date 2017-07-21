import os
import logging
import datetime
from flask import Flask, render_template, redirect, url_for, request, Response, send_file, abort
from flask_restplus import Resource, Api, fields
import monitor.webarchive
from monitor.status import load_service_status

app = Flask(__name__)


@app.route('/')
def index():
    return redirect('/status/dashboard', code=307)


@app.before_first_request
def setup_logging():
    if not app.debug:
        # In production mode, add log handler to sys.stderr.
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)


api = Api(app, version='1.0', title='UKWA Ingest API',
          description='API for interacting with UKWA ingest services.', doc="/doc/")

status_ns = api.namespace('status', description='Service Status Operations')


@status_ns.route('/dashboard')
class Dashboard(Resource):
    '''Shows a HTML dashboard that summarises service status'''
    @status_ns.doc(id='get_status_dashboard')
    @status_ns.response(200, 'A HTML dashboard summarising the current service status')
    def get(self):
        app.logger.info("GOT %s" % os.environ['LUIGI_STATE_FOLDER'])
        # Get services and status:
        services = load_service_status()

        # Log collected data:
        #app.logger.info(json.dumps(services, indent=4))

        # And render
        return Response(render_template('dashboard.html', title="Status", services=services), mimetype="text/html")


@status_ns.route('/map')
class Overview(Resource):
    '''Shows a map-style display that summarises service status'''
    @status_ns.doc(id='get_status_overview')
    @status_ns.response(200, 'A map-style display summarising the current service status')
    def get(self):
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


class FileSchema(fields.Raw):
    __schema_type__ = 'file'

rend_ns = api.namespace('rendered', description='Access rendered web resources')


@rend_ns.route('/original')
class RenderedOriginals(Resource):

    """
    Grabs a rendered original resource as captured at harvest time.

    Only reason Wayback can't do this is that it does not like the extended URIs
    i.e. 'screenshot:http://' and replaces them with 'http://screenshot:http://'
    """
    @rend_ns.doc(id='get_rendered_original', model=FileSchema)
    @rend_ns.response(200, 'The rendered version of the original URL.')
    @rend_ns.response(404, 'If no screenshot for that url has been archived.')
    @rend_ns.param('url', 'The URL to look for.  Note that this requires an exact match, '
                           'e.g. "https://www.bl.uk/" will work but "https://www.bl.uk" will not', required=True)
    @rend_ns.param('render_type', "The type or rendering to return. Can be 'screenshot', 'thumbnail, 'imagemap', 'onreadydom', 'har'.", required=True, default='screenshot')
    @rend_ns.param('target_date', "The target date. The closest date match will be returned.", required=True, default=datetime.datetime.today().isoformat())
    @api.representation('image/png')
    def get(self):
        # get the URL parameters
        url = request.args.get('url')
        render_type = request.args.get('render_type', 'screenshot')
        target_date_str = request.args.get('target_date', datetime.datetime.today().isoformat())
        target_date = datetime.datetime.strptime(target_date_str, "%Y-%m-%dT%H:%M:%S.%f")

        # Look up the item via the CDX index:
        stream, content_type = monitor.webarchive.get_rendered_original(url, render_type, target_date)

        # If it's not found:
        if stream is None:
            return Response(response="No such rendering found.", content_type='text/plain', status=404)

        return send_file(stream, mimetype=content_type)


if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0", use_reloader=False)
