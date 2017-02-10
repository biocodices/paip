from subprocess import run, PIPE
from datetime import datetime

from humanfriendly import format_timespan


def run_command(command, logfile=None, append=False, log_stdout=True,
                log_stderr=True):
    """
    Accepts a *command* and runs it in the shell. Returns (STDOUT, STDERR).
    If the command fails, an Exception will be raised.

    Pass a *logfile* to write STDERR and STDOUT outputs to a given filepath.
    You can choose not to write them to the logfile with log_stdout=False
    and/or log_stderr=False (they will still be returned as a tuple).

    If logging to a file, by default the logfile will be truncated. You can
    append to the logfile instead by setting append=True.
    """
    if logfile:
        start_time = datetime.now()
        log_separator = '-' * 10

        with open(logfile, ('a' if append else 'w')) as f:
            f.write('{} TIME\n\n{}\n\n'.format(log_separator, start_time))
            f.write('{} COMMAND\n\n{}\n\n'.format(log_separator, command))

    result = run(command, shell=True, check=True, stdout=PIPE, stderr=PIPE)

    stdout = result.stdout
    stderr = result.stderr

    if logfile:
        end_time = datetime.now()
        elapsed_time = format_timespan((end_time - start_time).seconds)

        with open(logfile, 'a') as f:

            if log_stdout:
                stdout = stdout.decode().strip()
                f.write('{} STDOUT\n\n{}\n\n'.format(log_separator, stdout))

            if log_stderr:
                stderr = stderr.decode().strip()
                f.write('{} STDERR\n\n{}\n\n'.format(log_separator, stderr))

            f.write('{} END\n\nFinished at {}\nTook {}\n'
                    .format(log_separator, end_time, elapsed_time))

    return (stdout, stderr)

