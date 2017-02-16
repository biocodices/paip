from os import listdir
from os.path import isdir, basename, join, expanduser, abspath

import luigi

from paip.task_types import BaseTask


class CohortTask(BaseTask):
    """
    This class is meant as a second parent class for luigi Tasks that deal
    with a group of samples (e.g. JointGenotyping). It adds some utilities
    to search for all (or some) samples' files and output/log to the root
    dir, parent of all samples.

    For simplicity's sake, the code will assume the task is run from the
    parent dir of all samples subdirectories.
    """
    basedir = luigi.Parameter(default='.')
    samples = luigi.Parameter()

    def __init__(self, **kwargs):
        super(BaseTask, self).__init__(**kwargs)
        self.basedir = abspath(expanduser(self.basedir))
        self.samples = self._find_samples(self.samples, self.basedir)
        if not self.samples:
            raise EmptyCohortException('No samples found in: {}'
                                       .format(self.basedir))
        self.cohort_name = self._define_cohort_name()

    def log_path(self, log_name):
        """Generate a log_path from *log_name* and self.cohort_name."""
        return '{}.log.{}'.format(self.cohort_name, log_name)

    @staticmethod
    def _find_samples(samples, basedir):
        """
        Check for the *samples* in the basedir. 'ALL' will make it
        find every subdir in the CWD and return those dir names as sample
        names, while a list of comma-separated sample names will trigger a
        check of the sample's existence as subdirs and return only those
        in a list.
        """
        available_samples = [name for name in sorted(listdir(basedir))
                             if isdir(join(basedir, name))]

        if samples == 'ALL':
            return available_samples

        chosen_samples = samples.split(',')

        for sample in chosen_samples:
            if sample not in available_samples:
                raise ValueError("Sample '{}' not found in: {}. "
                                 'Available samples: {}'
                                 .format(sample, basedir,
                                         ', '.join(available_samples)))

        return chosen_samples

    def _define_cohort_name(self):
        """
        Define the Cohort name from the self.basedir and the number of
        self.samples.
        """
        return '{}__{}_Samples'.format(basename(self.basedir),
                                       len(self.samples))


class EmptyCohortException(Exception):
    pass

