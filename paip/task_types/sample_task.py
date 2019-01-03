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

    # These keys are expected in the sequencing YAML associated with each run
    # unless it's an external job like a Macrogen exome or an IonTorrent panel:
    REQUIRED_SEQUENCING_DATA_KEYS = [
        "library_id",
        "platform",
        "platform_unit",
        "run_number",
        "flowcell_id",
        "lane_numbers_merged",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = self.sample
        self.dir = join(self.basedir, self.sample)
        self.store_sequencing_data()
        self.check_sequencing_data()

    def store_sequencing_data(self):
        """
        Put data from the YAML for this particular sample in self.
        """
        try:
            sample_data = self.sequencing_data[self.sample]
        except KeyError:
            available_samples = ', '.join(self.sequencing_data.keys())
            message = (f'Sample "{self.sample}" not found! '
                       f'Available samples are: {available_samples}.')
            raise SampleNotFoundError(message)

        for key, value in sample_data.items():
            setattr(self, key, value)

        self.external_exome = getattr(self, 'external_exome', False)
        self.ion = getattr(self, 'ion', False)

    def check_sequencing_data(self):
        """
        Check everything expected was found on the sequencing YAML file for
        this particular sample.
        """
        required_keys_missing = [
            key for key in self.REQUIRED_SEQUENCING_DATA_KEYS
            if not hasattr(self, key)
        ]
        if required_keys_missing and not (self.external_exome or self.ion):
            raise MissingDataInYML(
                f"Sample '{self.name}' is missing sequencing data: " +
                ', '.join(required_keys_missing) + '\n' +
                'Please add this in the sequencing YAML.')

    def cohort_params(self):
        """
        Return a copy of self.param_kwargs but without the 'sample' parameter.
        """
        params = self.param_kwargs.copy()
        del(params['sample'])
        return params


class SampleNotFoundError(Exception): pass
class MissingDataInYML(Exception): pass
