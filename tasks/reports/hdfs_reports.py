import os
import json
import datetime
import logging
import subprocess
import luigi
import luigi.contrib.hdfs
import luigi.contrib.ssh
from jinja2 import Environment, FileSystemLoader
from tasks.reports import TEMPLATE_DIR

logger = logging.getLogger('luigi-interface')

LUIGI_STATE_FOLDER = os.environ.get('LUIGI_STATE_FOLDER','./state')
INGEST_SERVICES_HOST = "ingest"


def state_file_path(date, tag, suffix):
    path = os.path.join( '/root/github/python-shepherd/state',
                         date.strftime("%Y-%m"),
                         tag,
                         '%s-%s' % (date.strftime("%Y-%m-%d"), suffix))
    return path


class RemoteHDFSListing(luigi.ExternalTask):
    """
    Looks for the file on the Ingest Services server that holds the current HDFS listing.

    For file_list, can be e.g. 'all', 'empty', 'warc', 'warc-ukwa', 'warc-duplicate', 'warc-ukwa-duplicate'.
    """
    date = luigi.DateParameter(default=datetime.date.today())
    file_list = luigi.Parameter(default="all")

    def output(self):
        path = state_file_path(self.date, 'hdfs', '%s-files-list.jsonl' % self.file_list)
        return luigi.contrib.ssh.RemoteTarget(path=path, host=INGEST_SERVICES_HOST)


class GenerateHDFSReport(luigi.Task):
    """
    Takes the file lists and creates a HTML report.
    """
    date = luigi.DateParameter(default=datetime.date.today())

    def remote_target(self, file_list="all"):
        path = state_file_path(self.date, 'hdfs', '%s-files-list.jsonl' % file_list)
        return luigi.contrib.ssh.RemoteTarget(path=path, host=INGEST_SERVICES_HOST)

    def output(self):
        return luigi.LocalTarget("/var/www/html/hdfs-reports/%s.html" % self.date.strftime("%Y-%m-%d"))

    def output_link(self):
        return "/var/www/html/hdfs-reports/index.html"

    def complete(self):
        """
        TODO Check if the HDFS report file is in place and there is an index symlink pointing to it.
        :return:
        """
        if not self.output().exists():
            return False
        if not os.path.exists(self.output_link()):
            return False
        if os.readlink(self.output_link()) != self.output().path:
            return False

        return True

    def run(self):
        # Read remote targets:
        empty_files = []
        empty_files_total = 0
        with self.remote_target().open() as f:
            for line in f:
                empty_files_total += 1
                item = json.loads(line)
                if item['filename'].endswith('arc.gz'):
                    empty_files.append(item)

        # Create the jinja2 environment.
        j2_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR),
                             trim_blocks=True)
        out = j2_env.get_template('hdfs_summary.html').render(
            title='HDFS Summary on %s' % self.date,
            empty_files= empty_files,
            empty_files_total=empty_files_total
        )

        # Write to a file:
        with self.output().open('w') as f:
            f.write(out)

        # And update the index symlink:
        if os.path.exists(self.output_link()):
            os.remove(self.output_link())
        os.symlink(self.output().path, self.output_link())


if __name__ == '__main__':
    luigi.run(['GenerateHDFSReport'])
