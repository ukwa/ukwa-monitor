import json
import logging
import datetime
from tasks.monitor import CheckStatus

logger = logging.getLogger(__name__)


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
            logger.info("Could not load %i mins ago... %s" % (mins, e))
            #app.logger.exception(e)

        if services is not None:
            break

    if services is None:
        raise Exception("Could not load a recent service status file!")

    return services


def load_services(json_file):
    logger.info("Attempting to load %s" % json_file)
    with open(json_file, 'r') as reader:
        services = json.load(reader)
    return services

