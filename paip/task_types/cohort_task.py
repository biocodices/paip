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
        self.sample_list = self._find_samples(self.samples)

        if not self.sample_list:
            raise EmptyCohortException('No samples found in: {}'
                                       .format(self.basedir))

        known_pipes = ['all_sites', 'variant_sites', 'target_sites']
        if self.pipeline_type not in known_pipes:
            raise ValueError('Unknown pipeline_type "{}". Known types are: {}'
                             .format(self.pipeline_type,
                                     ', '.join(known_pipes)))

        self.cohort_name = self._define_cohort_name()

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
        # Use in classes that also inherit from luigi.WrapperTask. This
        # behavior is already packed in the helpers.create_cohort_task()
        #
        # TODO: There might be a way to implement this with the descriptor
        # protocol directly in create_cohort_task()
        sample_task_class = self.SAMPLE_REQUIRES

        for sample in self.sample_list:
            yield sample_task_class(sample=sample, **self.param_kwargs)

    def path(self, filename):
        """
        Generate a path to the given *filename* under the cohort's directory,
        using the cohort's name as a prefix and puting the pipeline_type
        in the name.
        """
        return join(self.basedir, '{}.{}.{}'.format(self.cohort_name,
                                                    self.pipeline_type,
                                                    filename))

    def cohort_path(self, filename):
        """Alias of self.path"""
        return self.path(filename)

    def sample_path(self, filename, sample=None):
        """
        Generate a path to the given *filename* under the given *sample*'s
        directory and with the sample's name as prefix.

        If no *sample* is passed, use the value of self.sample
        """
        if sample is None:
            sample = self.sample

        fn = '{0}/{0}.{1}.{2}'.format(sample, self.pipeline_type, filename)
        return join(self.basedir, fn)

    def _find_samples(self, samples):
        """
        Check for the *samples* in the basedir. 'ALL' will make it
        find every subdir in the CWD (as long as it's also found in
        self.sequencing_data) and return those dirnames as sample
        names, while a list of comma-separated sample names will trigger a
        check of the sample's existence as subdirs and return only those
        in a list.
        """
        available_samples = [name for name in sorted(listdir(self.basedir))
                             if isdir(join(self.basedir, name)) and
                             name in self.sequencing_data]

        if samples == 'ALL':
            return available_samples

        chosen_samples = samples.split(',')

        for sample in chosen_samples:
            if sample not in available_samples:
                raise ValueError("Sample '{}' not found in: {}. "
                                 'Available samples: {}'
                                 .format(sample, self.basedir,
                                         ', '.join(available_samples)))

        return chosen_samples

    def _define_cohort_name(self):
        """
        Define the Cohort name from the self.basedir and the number of
        self.sample_list.
        """
        return '{}__{}_Samples'.format(basename(self.basedir),
                                       len(self.sample_list))


class EmptyCohortException(Exception):
    pass

