from os import rename
from os.path import abspath, expanduser
import yaml

from paip.helpers import (
    generate_command,
    run_command,
)


class SampleTask:
    """
    This class is meant as a second parent class for luigi Tasks that deal
    with a single sample's files. It adds some utilities to generate paths
    for output files and for log files.
    """

    def sample_path(self, filename):
        """
        Generate a path to the given *filename* under self.sample_id's
        directory, using self.sample_id as a prefix. Example:

            > sample_path('foo.txt')  # => SampleX/SampleX.foo.txt

        """
        return '{0}/{0}.{1}'.format(self.sample_id, filename)

    def sample_paths(self, templates):
        return [self.sample_path(template) for template in templates]

    def log_path(self, log_name):
        """
        Generate the filename for the logs with the passed name, adding
        the dir and prefix of self.sample_id. Example:

            > log_path('foo')  # => 'sample_X/sample_X.log.foo'

        """
        return self.sample_path('log.{}'.format(log_name))

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

    def load_sample_data_from_yaml(self, yml_path):
        """
        Given a path to a YAML file, read every key under self.sample_id and
        add it to self as a new attribute. For instance, if the YAML file
        looks like this:

            S1:
                library_id: Lib1
                sequencing_id: Seq1
                id_in_sequencing: Spl1

        This method will work this way:

            > sample_task.sample_id == 'S1'  # => True
            > sample_task.load_sequencing_data_from_yaml('/path/to/data.yml')
            > sample_task.library_id  # => 'Lib1'
            > sample_task.sequencing_id  # => 'Seq1'
            > sample_task.id_in_sequencing  # => 'Spl1'

        """
        with open(abspath(expanduser(yml_path))) as f:
            data = yaml.load(f)

        data = data[self.sample_id]

        for key in data.keys():
            setattr(self, key, data[key])

