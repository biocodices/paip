from os.path import join

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dir = join(self.basedir, self.sample)

        sequencing_data = self.sequencing_data[self.sample]
        for key in sequencing_data.keys():
            setattr(self, key, sequencing_data[key])

    def path(self, filename):
        return join(self.dir, '{}.{}'.format(self.sample, filename))

    def sample_pipeline_path(self, filename):
        """
        Generate a path to the given filename under the sample's directory
        and include the pipeline type in the filename. Example:

            > sample_path('foo.txt')  # => SampleX/SampleX.foo.txt

        """
        return join(self.dir, '{}.{}.{}'.format(self.sample,
                                                self.pipeline_type,
                                                filename))

    def sample_path(self, filename):
        """
        Generate a path to the given *filename* under self.sample's
        directory, using self.sample as a prefix. Example:

            > sample_path('foo.txt')  # => SampleX/SampleX.foo.txt

        """
        return self.path(filename)

    def sample_paths(self, filenames):
        """Alias of self.paths"""
        return self.paths(filenames)

