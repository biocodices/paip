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

    def rename_temp_idx(self):
        """
        Some tasks generate a idx file alongside the vcf output, by
        adding '.idx' to the vcf filename. We rename the temporary
        idx file generated here. Assumes self.temp_vcf has been defined.
        """
        suffix = '.idx'
        output_vcf = self._find_output('.vcf').fn
        intended_filename = output_vcf + suffix
        temp_filename = self.temp_vcf + suffix
        rename(temp_filename, intended_filename)

    def rename_temp_bai(self):
        """
        Some tasks generate a bai file alongside the bam output, by
        adding '.bai' to the vcf filename. We rename the temporary
        bai file generated here. Assumes self.temp_bam has been defined.
        """
        suffix = '.bai'
        output_bam = self._find_output('.bam').fn
        intended_filename = output_bam + suffix
        temp_filename = self.temp_bam + suffix
        rename(temp_filename, intended_filename)

    def _find_output(self, substring):
        """
        Returns the first output that matches the given substring.
        """
        outfiles = self.output()

        if not isinstance(outfiles, list):
            outfiles = [outfiles]

        for outfile in outfiles:
            if substring in outfile.fn:
                return outfile

        raise ValueError('No output file found that matches "{}"'
                         .format(substring))

