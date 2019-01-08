import luigi

from paip.task_types import SampleTask
from paip.helpers.create_cohort_task import create_cohort_task


class BamPresent(luigi.ExternalTask, SampleTask):
    """
    Expects a IonTorrent-generated BAM file from a single sample.
    """
    OUTPUT = 'ion.bam'


BamPresentCohort = create_cohort_task(BamPresent)
