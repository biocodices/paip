from os.path import expanduser, join, dirname
from os import environ

import luigi
import coloredlogs


def set_luigi_logging():
    """
    Hack to replace luigi's default logger config with a custom
    file. The details of that file are not relevant really,
    because the actual log config will come from coloredlogs.
    But stepping over luigi's logger config like this is necessary
    because otherwise I get duplicated logging output.
    """
    basedir = dirname(__file__)
    config_file = join(dirname(basedir), 'example_config', 'luigi_logging.conf')

    # Docs for luigi interface:
    # http://luigi.readthedocs.io/en/stable/api/luigi.interface.html
    luigi.interface.setup_interface_logging(
        conf_file=expanduser(config_file)
    )
    log_format = '[%(asctime)s] @%(hostname)s %(message)s'
    coloredlogs.DEFAULT_LOG_FORMAT = log_format
    coloredlogs.install(level=environ.get('LOG_LEVEL') or 'INFO')

