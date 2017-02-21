import luigi

from paip.helpers import (
    generate_command,
    run_command,
)


class BaseTask(luigi.Task):
    """
    Base class for SampleTask and CohortTask, provides shared logic to
    run commands and rename temporary output files.
    """
    def log_path(self, log_name):
        """Generate the filepath for a log with the given *log_name*."""
        return 'log.{}'.format(log_name)

    def run_program(self, program_name, program_options, **kwargs):
        """
        Will generate a command to run in the shell for *program_name* with
        *program_options*. Extra kwargs are passed to run_command().

        The name of the current class (that is, a luigi.Task) will be used
        as the name for the logfile.

        Returns the ouptut from run_command(), namely a tuple with
        (STDOUT, STDERR).
        """
        command = generate_command(program_name, program_options)
        logfile = self.log_path(self.__class__.__name__)
        command_result = run_command(command, logfile=logfile, **kwargs)
        return command_result

