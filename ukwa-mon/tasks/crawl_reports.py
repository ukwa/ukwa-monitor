import os
import time
import logging
import datetime
import tempfile
import luigi
import luigi.date_interval
import luigi.contrib.hdfs
import luigi.contrib.hadoop
import luigi.contrib.hadoop_jar

from tasks.reports.plotto import generate_crawl_summary

logger = logging.getLogger('luigi-interface')

CRAWL_STATS_PREFIX="/user/root/task-state"


def get_modest_interval():
    return luigi.date_interval.Custom(
        datetime.date.today() - datetime.timedelta(days=14),
        datetime.date.today() + datetime.timedelta(days=1))


class ScanForOutputs(luigi.WrapperTask):
    """
    This task scans the output folder for jobs and instances of those jobs, looking for crawled content to process.

    Sub-class this and override the scan_job_launch method as needed.
    """
    task_namespace = 'scan'
    date_interval = luigi.DateIntervalParameter(default=get_modest_interval())
    timestamp = luigi.DateMinuteParameter(default=datetime.datetime.today())

    def requires(self):
        # Enumerate the jobs:
        for (job, launch) in self.enumerate_launches():
            #logger.debug("Yielding %s/%s" % ( job, launch ))
            yield self.process_output(job, launch)

    def enumerate_launches(self):
        # Get HDFS client:
        client = luigi.contrib.hdfs.WebHdfsClient()
        # Look for jobs that need to be processed:
        for date in self.date_interval:
            logger.info("Scanning date %s..." % date)
            for job_item in client.listdir(CRAWL_STATS_PREFIX):
                job = os.path.basename(job_item)
                launch_glob = date.strftime('%Y%m%d')
                logger.debug("Looking for job launch folders matching %s in %s/%s" %
                             (launch_glob, CRAWL_STATS_PREFIX, job))
                for launch_item in client.listdir("%s/%s" % (CRAWL_STATS_PREFIX, job)):
                    logger.debug("Looking at %s" % launch_item)
                    launch = os.path.basename(launch_item)
                    if launch.startswith(launch_glob):
                        yield (job, launch)


class ScanForCrawlStats(ScanForOutputs):
    """
    This task scans the output folder for jobs and instances of those jobs, looking for crawls logs.
    """
    task_namespace = 'scan'

    def process_output(self, job, launch):
        #a_summary_file = '../../tasks/process/test-data/weekly-20170220090024-crawl-logs-14.analysis.tsjson.sorted'
        #generate_crawl_summary('weekly', '20170220090024', a_summary_file, './report-tmp')
        print(job, launch)


if __name__ == '__main__':
    luigi.run(['scan.ScanForCrawlStats', '--local-scheduler'])
