import luigi

from paip.task_types import SampleTask


class CheckFastqs(luigi.ExternalTask, SampleTask):
    """
    Expects fastq files with forward and reverse reads of the same
    sample.
    """
    OUTPUT = ['R1.fastq', 'R2.fastq']

