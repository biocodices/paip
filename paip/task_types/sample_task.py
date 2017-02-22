from os.path import abspath, expanduser, join
import yaml

import luigi

from paip.task_types import BaseTask


class SampleTask(BaseTask):
    """
    This class is meant as a subclass of luigi Tasks that deal with a single
    sample's files. It adds some utilities to generate paths for output files
    and for log files.

    To use it, it's enough to define a subclass that defines a run() method,
    and REQUIRES and OUTPUT class variables.
    """
    sample = luigi.Parameter()
    basedir = luigi.Parameter(default='.')

    def __init__(self, **kwargs):
        super(BaseTask, self).__init__(**kwargs)
        self.basedir = abspath(expanduser(self.basedir))
        self.dir = join(self.basedir, self.sample)

    def output(self):
        """
        Take the filename in self.OUTPUT and return it as a path to that
        file in the sample's dir, and wrapped as a luigi.LocalTarget.

        If self.OUTPUT has a list of filenames, return a list too.
        """
        if isinstance(self.OUTPUT, list):
            return [luigi.LocalTarget(self.sample_path(fn))
                    for fn in self.OUTPUT]

        return luigi.LocalTarget(self.sample_path(self.OUTPUT))

    def sample_path(self, filename):
        """
        Generate a path to the given *filename* under self.sample's
        directory, using self.sample as a prefix. Example:

            > sample_path('foo.txt')  # => SampleX/SampleX.foo.txt

        """
        return join(self.dir, '{0}.{1}'.format(self.sample, filename))

    def sample_paths(self, templates):
        return [self.sample_path(template) for template in templates]

    def log_path(self, log_name):
        """
        Generate the filename for the logs with the passed name, adding
        the dir and prefix of self.sample. Example:

            > log_path('foo')  # => 'sample_X/sample_X.log.foo'

        """
        return self.sample_path('log.{}'.format(log_name))

    def load_sample_data_from_yaml(self, yml_filename):
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
        with open(join(self.basedir, yml_filename)) as f:
            data = yaml.load(f)

        data = data[self.sample]

        for key in data.keys():
            setattr(self, key, data[key])

