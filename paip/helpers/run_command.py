from subprocess import run, PIPE
from datetime import datetime

from humanfriendly import format_timespan


def run_command(command, logfile=None, append=False, capture_stdout=True,
                capture_stderr=True):
    """
    Accepts a *command* and runs it in the shell. If the command fails, an
    Exception will be raised. Pass a *logfile* to write STDERR and STDOUT
    outputs to a given filepath. Optionally, disable those redirections
    with capture_stdout=False and/or capture_stderr=False.

    By default the logfile is truncated. You can append to the logfile with
    append=True.
    """
    if logfile:
        start_time = datetime.now()
        log_separator = '-' * 10

        with open(logfile, ('a' if append else 'w')) as f:
            f.write('{} TIME\n\n{}\n\n'.format(log_separator, start_time))
            f.write('{} COMMAND\n\n{}\n\n'.format(log_separator, command))

    # This will capture the STDOUT and/or STDERR to put it in the logfile:
    stdout_option = PIPE if capture_stdout else None
    stderr_option = PIPE if capture_stderr else None

    result = run(command, shell=True, check=True,
                 stdout=stdout_option, stderr=stderr_option)

    stdout = result.stdout is not None and result.stdout.decode().strip()
    stderr = result.stderr is not None and result.stderr.decode().strip()

    if logfile:
        end_time = datetime.now()
        elapsed_time = format_timespan((end_time - start_time).seconds)

        with open(logfile, 'a') as f:

            if capture_stdout and stdout:
                f.write('{} STDOUT\n\n{}\n\n'.format(log_separator, stdout))

            if capture_stderr and stderr:
                f.write('{} STDERR\n\n{}\n\n'.format(log_separator, stderr))

            f.write('{} END\n\nFinished at {}\nTook {}\n'
                    .format(log_separator, end_time, elapsed_time))

    return (stdout, stderr)

