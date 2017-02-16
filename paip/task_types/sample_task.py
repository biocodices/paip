from os.path import abspath, expanduser
import yaml

import luigi

from paip.task_types import BaseTask


class SampleTask(BaseTask):
    """
    This class is meant as a subclass of luigi Tasks that deal with a single
    sample's files. It adds some utilities to generate paths for output files
    and for log files.
    """
    sample = luigi.Parameter()

    def sample_path(self, filename):
        """
        Generate a path to the given *filename* under self.sample's
        directory, using self.sample as a prefix. Example:

            > sample_path('foo.txt')  # => SampleX/SampleX.foo.txt

        """
        return '{0}/{0}.{1}'.format(self.sample, filename)

    def sample_paths(self, templates):
        return [self.sample_path(template) for template in templates]

    def log_path(self, log_name):
        """
        Generate the filename for the logs with the passed name, adding
        the dir and prefix of self.sample. Example:

            > log_path('foo')  # => 'sample_X/sample_X.log.foo'

        """
        return self.sample_path('log.{}'.format(log_name))

    def load_sample_data_from_yaml(self, yml_path):
        """
        Given a path to a YAML file, read every key under self.sample and
        add it to self as a new attribute. For instance, if the YAML file
        looks like this:

            S1:
                library_id: Lib1
                sequencing_id: Seq1
                id_in_sequencing: Spl1

        This method will work this way:

            > sample_task.sample == 'S1'  # => True
            > sample_task.load_sequencing_data_from_yaml('/path/to/data.yml')
            > sample_task.library_id  # => 'Lib1'
            > sample_task.sequencing_id  # => 'Seq1'
            > sample_task.id_in_sequencing  # => 'Spl1'

        """
        with open(abspath(expanduser(yml_path))) as f:
            data = yaml.load(f)

        data = data[self.sample]

        for key in data.keys():
            setattr(self, key, data[key])

