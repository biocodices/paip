import time
import os
from os.path import join, expanduser, abspath
import yaml

import luigi

from paip.helpers import (
    Config,
    generate_command,
    run_command,
    get_running_tasks,
)


class BaseTask(luigi.Task):
    """
    Base class for SampleTask and CohortTask, provides shared logic to
    run commands and rename temporary output files.
    """

    # IMPORTANT:
    #
    # If you change any of these parameter defaults, please update the
    # docstring at the top of paip/run_task.py!

    basedir = luigi.Parameter(default='.')

    # The following parameters are used in different places. Not all tasks
    # make use of all of them, but it seemed cleaner to add them once
    # here instead of having them scattered over different tasks/files:
    samples = luigi.Parameter(default='ALL')
    pipeline_type = luigi.Parameter(default='variant_sites')
    min_gq = luigi.IntParameter(default=30)
    min_dp = luigi.IntParameter(default=30)
    num_threads = luigi.IntParameter(default=1)

    # This parameter gives you extra flexibility for the trimming step
    trim_software = luigi.Parameter(default='cutadapt')

    # Override in child classes to automatically define an output() method:
    OUTPUT = None
    OUTPUT_RENAMING = None

    # Override in child classes to put outputs in a subdirectory:
    SUBDIR = None

    # Override in child classes to only allow a number of simultaneous
    # tasks of that type to be running at the same time:
    MAX_CONCURRENT_TASKS = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.basedir = abspath(expanduser(self.basedir))
        self.sequencing_data = self.load_sample_data_from_yaml()
        self.config = Config(custom_config_dir=self.basedir)

        if self.SUBDIR:
            os.makedirs(join(self.basedir, self.SUBDIR), exist_ok=True)

    def requires(self):
        """
        Assumes that self.REQUIRES is defined.

        Take the class or classes in self.REQUIRES and initialize them
        with self.param_kwargs as parameters.

        Returns a single object or a list, according to what finds in
        self.REQUIRES.
        """
        if isinstance(self.REQUIRES, list):
            return [require(**self.param_kwargs) for require in self.REQUIRES]

        if isinstance(self.REQUIRES, dict):
            return {key: require(**self.param_kwargs)
                    for key, require in self.REQUIRES.items()}

        return self.REQUIRES(**self.param_kwargs)

    def output(self):
        """
        (This will be called only if the Task that inherits from BaseTask
        does not define an output method)

        Take the filename in self.OUTPUT and return it as a luigi.LocalTarget
        that points to that filename in the sample's/cohort's directory.

        If self.OUTPUT has a list of filenames, a list of targets will be
        returned instead.

        If self.OUTPUT is not defined, the task is expected to define its own
        customn output() method that will override this one.

        If self.SUBDIR is defined, the filepaths will be in it that
        subdirectory.

        If no self.OUTPUT constant is defined, look for a self.OUTPUT constant
        that should be a tuple of strings. Use both values for a replace
        operation on the input file (replace the first value with the second
        value). This only works for input tasks that have a single file as
        output!
        """
        if self.OUTPUT:
            targets = self.make_targets_from_OUTPUT(self.OUTPUT)
        elif self.OUTPUT_RENAMING:
            targets = self.make_targets_from_OUTPUT_RENAMING(self.OUTPUT_RENAMING)
        else:
            raise Exception(
                'Please define an output methodm, an OUTPUT constant or an '
                'OUTPUT_RENAMING constant for the class {}'
                .format(self.__class__.__name__))
        return targets

    def make_targets_from_OUTPUT_RENAMING(self, old_value_new_value):
        # This assumes there's only ONE input file!
        if not isinstance(self.input(), luigi.LocalTarget):
            raise ValueError('OUTPUT_RENAMING only works for tasks with a '
                             'single input task that produces a single target '
                             'as output!')
        input_path = self.input().path
        old_value, new_value = old_value_new_value
        output_path = input_path.replace(old_value, new_value)
        return luigi.LocalTarget(output_path)

    def make_targets_from_OUTPUT(self, out):
        if isinstance(out, list):
            targets = [luigi.LocalTarget(self.path(fn))
                       for fn in out]
        elif isinstance(out, dict):
            targets = {key: luigi.LocalTarget((self.path(fn)))
                       for key, fn in out.items()}
        elif isinstance(out, str):
            targets = luigi.LocalTarget(self.path(out))
        else:
            raise ValueError("I can't deal with this type of OUTPUT: "
                             f"{type(out)}")
        return targets

    def path(self, filename, prefix=True):
        """
        Return the filepath to the given *filename* under this sample or
        cohort directory (self.dir) and subdirectory, if self.SUBDIR is
        defined.

        The sample/cohort name is used as a prefix of the *filename* by
        default, unless *prefix* is set to False.
        """
        root = self.dir if not self.SUBDIR else join(self.dir, self.SUBDIR)

        if prefix:
            filename = '{}.{}'.format(self.name, filename)

        return join(root, filename)

    def paths(self, filenames):
        """
        Call self.path for each filename in *filenames*.
        """
        return [self.path(filename) for filename in filenames]

    def log_path(self, log_name):
        """
        Generate the filepath for a log with the given *log_name*.
        """
        return self.path('log.{}'.format(log_name))

    def run_program(self, program_name, program_options={}, **kwargs):
        """
        Will generate a command to run in the shell for *program_name* with
        *program_options*. Extra kwargs are passed to run_command().

        The name of the current class (that is, a luigi.Task) will be used
        as the name for the logfile.

        Returns the ouptut from run_command(), namely a tuple with
        (STDOUT, STDERR).
        """
        program_options.update({'num_threads': self.num_threads})
        command = generate_command(program_name, program_options, self.config)
        logfile = self.log_path(self.__class__.__name__)
        # TODO: implement this correctly:
        # self.sleep_until_available_to_run()
        command_result = run_command(command, logfile=logfile, **kwargs)
        return command_result

    def rename_temp_idx(self):
        """
        Some tasks generate a idx file alongside the vcf output, by
        adding '.idx' to the vcf filename. We rename the temporary
        idx file generated here. Assumes self.temp_vcf has been defined.
        """
        suffix = '.idx'
        output_vcf = self._find_output('.vcf').path
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
        output_bam = self._find_output('.bam').path
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
            if substring in outfile.path:
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
                run_number: Seq1
                id_in_sequencing: Spl1

        This method will work this way:

            > sample_task.sample == 'S1'  # => True
            > sample_task.load_sequencing_data_from_yaml('data.yml')
            > sample_task.library_id  # => 'Lib1'
            > sample_task.run_number  # => 'Seq1'
            > sample_task.id_in_sequencing  # => 'Spl1'

        """
        fp = join(self.basedir, yml_filename)

        try:
            with open(fp) as f:
                data = yaml.load(f) or {}
        except IOError:
            msg = ("I couldn't find this YAML file:\n\n{}\n\n"
                   'Make sure you are in the base directory of the Cohort\n'
                   'and create that file with info about the samples in this\n'
                   'sequencing. The sample IDs should be first level keys\n'
                   'and each sample must have these keys:\n\nSampleX:  \n'
                   '  library_id: ...\n  run_number: ...\n  '
                   'id_in_sequencing: ...\n  platform: ...\n  '
                   'platform_unit: ...\n  lane_numbers_merged: ...\n')
            raise IOError(msg.format(fp))

        return data

    @classmethod
    def running_tasks_of_this_class(cls):
        """
        Return the number of running tasks of this class.
        """
        this_class_name = cls.__name__
        running_now = [task for task in get_running_tasks()
                       if task == this_class_name]
        return len(running_now)

    @classmethod
    def sleep_until_available_to_run(cls):
        """
        Sleep until the number of running tasks of this class is less than
        cls.MAX_CONCURRENT_TASKS.
        """
        if cls.MAX_CONCURRENT_TASKS is None:
            return

        while cls.running_tasks_of_this_class() >= cls.MAX_CONCURRENT_TASKS:
            time.sleep(10)

