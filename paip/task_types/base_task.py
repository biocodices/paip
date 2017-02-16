from os import rename

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

    def rename_extra_temp_output_file(self, suffix):
        """
        In some tasks we use a self.temp_output_path as a temporary output
        for the GATK running program. Luigi handles the renaming of the
        temporary output file to the proper output file (self.output()).
        However, GATK sometimes generates a second file with a *suffix* using
        the temporary path as a base, and Luigi is not aware of this second
        file that also needs renaming. We deal with that file in this method.
        """
        temp_filename = self.temp_output_path + suffix
        intended_filename = self.output().fn + suffix
        rename(temp_filename, intended_filename)

