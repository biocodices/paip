from os import listdir
from os.path import isdir, basename, join

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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dir = self.basedir
        self.name = basename(self.dir)
        self.sample_list = self._find_samples(self.samples)

        if not self.sample_list:
            raise EmptyCohortException('No samples found in: {}'
                                       .format(self.dir))

        known_pipes = ['all_sites', 'variant_sites', 'target_sites']
        if self.pipeline_type not in known_pipes:
            raise ValueError('Unknown pipeline_type "{}". Known types are: {}'
                             .format(self.pipeline_type,
                                     ', '.join(known_pipes)))

    def requires(self):
        if hasattr(self, 'SAMPLE_REQUIRES'):
            return list(self.sample_requires())
        else:
            return super().requires()

    def sample_requires(self):
        # This is a handy way of setting the required dependencies for
        # Cohort tasks that are only a wrapper around a SampleTask, which
        # should run for all the samples in the cohort. It lets us define
        # a CohortTask with just a class constant 'SAMPLE_REQUIRES'.
        #
        # Use in classes that also inherit from luigi.WrapperTask. This
        # behavior is already packed in the helpers.create_cohort_task()
        sample_task_class = self.SAMPLE_REQUIRES

        for sample in self.sample_list:
            yield sample_task_class(sample=sample, **self.param_kwargs)

    def sample_path(self, filename, sample=None):
        """
        Generate a path to the given *filename* under the given *sample*'s
        directory and with the sample's name as prefix.

        If no *sample* is passed, use the value of self.sample
        """
        if sample is None:
            sample = self.sample

        return join(self.dir, '{0}/{0}.{1}'.format(sample, filename))

    def _find_samples(self, samples):
        """
        Check for the *samples* in the dir. 'ALL' will make it
        find every subdir in the CWD (as long as it's also found in
        self.sequencing_data) and return those dirnames as sample
        names, while a list of comma-separated sample names will trigger a
        check of the sample's existence as subdirs and return only those
        in a list.
        """
        available_samples = [name for name in sorted(listdir(self.dir))
                             if isdir(join(self.dir, name)) and
                             name in self.sequencing_data]

        if samples == 'ALL':
            return available_samples

        chosen_samples = samples.split(',')

        for sample in chosen_samples:
            if sample not in available_samples:
                raise ValueError("Sample '{}' not found in: {}. "
                                 'Available samples: {}'
                                 .format(sample, self.dir,
                                         ', '.join(available_samples)))

        return chosen_samples

class EmptyCohortException(Exception):
    pass

