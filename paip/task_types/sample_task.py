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

        self.name = self.sample
        self.dir = join(self.basedir, self.sample)

        try:
            sequencing_data = self.sequencing_data[self.sample]
        except KeyError:
            available_samples = ', '.join(self.sequencing_data.keys())
            message = (f'Sample "{self.sample}" not found! '
                       f'Available samples are: {available_samples}.')
            raise SampleNotFoundError(message)

        for key in sequencing_data.keys():
            setattr(self, key, sequencing_data[key])

    def cohort_params(self):
        """
        Return a copy of self.param_kwargs but without the 'sample' parameter.
        """
        params = self.param_kwargs.copy()
        del(params['sample'])
        return params


class SampleNotFoundError(Exception):
    pass
