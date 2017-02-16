from subprocess import run, PIPE, CalledProcessError
from datetime import datetime
import logging

from humanfriendly import format_timespan


logger = logging.getLogger(__name__)


def run_command(command, logfile=None, log_append=False, log_stdout=True,
                log_stderr=True):
    """
    Accepts a *command* and runs it in the shell. Returns (STDOUT, STDERR).
    If the command fails, an Exception will be raised.

    Pass a *logfile* to write STDOUT and STDERR outputs to a given filepath.
    You can choose not to write them to the logfile with log_stdout=False
    and/or log_stderr=False (they will still be returned as a tuple).

    If logging to a file, by default the logfile will be truncated. You can
    append to the logfile instead by setting log_append=True.
    """
    if logfile:
        start_time = datetime.now()
        with open(logfile, ('a' if log_append else 'w')) as f:
            add_to_log('TIME', start_time, f)
            add_to_log('COMMAND', command, f)

    try:
        result = run(command, shell=True, check=True, stdout=PIPE, stderr=PIPE)
    except CalledProcessError as error:
        logger.error('This command failed (return code={}):\n{}'
                     .format(error.returncode, error.cmd))
        logger.error('STDOUT:\n{}'.format(error.output.decode().strip()))
        logger.error('STDERR:\n{}'.format(error.stderr.decode().strip()))
        raise

    stdout = result.stdout
    stderr = result.stderr

    if logfile:
        end_time = datetime.now()
        elapsed_time = format_timespan((end_time - start_time).seconds)

        with open(logfile, 'a') as f:

            if log_stdout:
                stdout = stdout.decode().strip()
                add_to_log('STDOUT', stdout, f)

            if log_stderr:
                stderr = stderr.decode().strip()
                add_to_log('STDERR', stderr, f)

            coda = ('Finished at {}\nTook {}' .format(end_time, elapsed_time))
            add_to_log('END', coda, f)

    return (stdout, stderr)


def add_to_log(section_name, content, file_handler):
    """Adds given *content* to the log under the *section_name*."""
    separator = '—' * 10
    message = ('{sep} {title}\n\n{content}\n\n'
               .format(sep=separator, title=section_name, content=content))
    file_handler.write(message)

