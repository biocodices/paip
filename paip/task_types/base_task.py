import os
from os.path import join, expanduser, abspath
import yaml

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
    basedir = luigi.Parameter(default='.')

    # These parameters are used in different places. Not all tasks
    # make use of all of them, but it seemed cleaner to add them once
    # here instead of all over different tasks:
    samples = luigi.Parameter(default='ALL')
    pipeline_type = luigi.Parameter(default='variant_sites')
    min_gq = luigi.IntParameter(default=30)
    min_dp = luigi.IntParameter(default=30)

    # This parameter gives you extra flexibility for the trimming step
    trim_software = luigi.Parameter(default='cutadapt')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.basedir = abspath(expanduser(self.basedir))
        self.sequencing_data = self.load_sample_data_from_yaml()

    def requires(self):
        """
        Take the class or classes in self.REQUIRES and initialize them
        with this class parameters. Returns a single object or a list
        according to what finds in self.REQUIRES.
        """
        if isinstance(self.REQUIRES, list):
            return [require(**self.param_kwargs) for require in self.REQUIRES]

        return self.REQUIRES(**self.param_kwargs)

    def output(self):
        """
        Take the filename in self.OUTPUT and return it as a path to that
        file in the sample's dir, and wrapped as a luigi.LocalTarget.

        If self.OUTPUT has a list of filenames, return a list too.
        """
        if not hasattr(self, 'OUTPUT'):
            return

        if isinstance(self.OUTPUT, list):
            return [luigi.LocalTarget(self.path(fn)) for fn in self.OUTPUT]

        return luigi.LocalTarget(self.path(self.OUTPUT))

    def path(self):
        raise NotImplementedError

    def paths(self, filenames):
        return [self.path(filename) for filename in filenames]

    def log_path(self, log_name):
        """Generate the filepath for a log with the given *log_name*."""
        return self.path('log.{}'.format(log_name))

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
        os.rename(temp_filename, intended_filename)
        # ^ Leave this as os.rename, don't import rename directly,
        # so it can be mocked in the tests:

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
        os.rename(temp_filename, intended_filename)
        # ^ Leave this as os.rename, don't import rename directly,
        # so it can be mocked in the tests:

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

    def load_sample_data_from_yaml(self, yml_filename='sequencing_data.yml'):
        """
        Given a filename of a YAML file, find it in the self.basedir,
        read every key under self.sample and add it to self as a new
        attribute. For instance, if the YAML file looks like this:

            S1:
                library_id: Lib1
                sequencing_id: Seq1
                id_in_sequencing: Spl1

        This method will work this way:

            > sample_task.sample == 'S1'  # => True
            > sample_task.load_sequencing_data_from_yaml('data.yml')
            > sample_task.library_id  # => 'Lib1'
            > sample_task.sequencing_id  # => 'Seq1'
            > sample_task.id_in_sequencing  # => 'Spl1'

        """
        fp = join(self.basedir, yml_filename)

        try:
            with open(fp) as f:
                data = yaml.load(f)
        except IOError:
            msg = ("I couldn't find this YAML file:\n\n{}\n\n"
                   'Make sure you are in the base directory of the Cohort\n'
                   'and create that file with info about the samples in this\n'
                   'sequencing. The sample IDs should be first level keys\n'
                   'and each sample must have these keys:\n\nSampleX:  \n'
                   '  library_id: ...\n  sequencing_id: ...\n  '
                   'id_in_sequencing: ...\n  platform: ...\n  '
                   'platform_unit: ...\n')
            raise IOError(msg.format(fp))

        return data

