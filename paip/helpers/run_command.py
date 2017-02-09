from subprocess import run, PIPE
from datetime import datetime

from humanfriendly import format_timespan


def run_command(command, logfile=None, log_stderr=True, log_stdout=True,
                append=False):
    """
    Accepts a *command* and runs it in the shell. If the command fails, an
    Exception will be raised. Pass a *logfile* to put STDERR and STDOUT outputs
    in a file. Optionally, disable one of those redirections with
    log_stdout=False or log_stderr=False.

    If append=True, the logfile will not be overwritten but appended to.
    """
    log_separator = '-' * 10

    if logfile:
        start_time = datetime.now()

        with open(logfile, ('a' if append else 'w')) as f:
            f.write('{} TIME\n\n{}\n\n'.format(log_separator, start_time))
            f.write('{} COMMAND\n\n{}\n\n'.format(log_separator, command))

    result = run(command, shell=True, check=True, stdout=PIPE, stderr=PIPE)

    stdout = result.stdout.decode().strip()
    stderr = result.stderr.decode().strip()

    if logfile:
        end_time = datetime.now()
        elapsed_time = format_timespan((end_time - start_time).seconds)

        with open(logfile, 'a') as f:

            if log_stdout and stdout:
                f.write('{} STDOUT\n\n'.format(log_separator))
                f.write(stdout)
                f.write('\n\n')

            if log_stderr and stderr:
                f.write('{} STDERR\n\n'.format(log_separator))
                f.write(stderr)
                f.write('\n\n')

            f.write('{}\n\n'.format(log_separator))
            f.write('Finished at {}\n'.format(end_time))
            f.write('Took {}\n'.format(elapsed_time))

    return (stdout, stderr)

