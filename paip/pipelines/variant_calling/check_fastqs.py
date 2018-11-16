import luigi

from paip.task_types import SampleTask


class CheckFastqs(luigi.ExternalTask, SampleTask):
    """
    Expects fastq files with forward and reverse reads of the same
    sample.
    """
    OUTPUT = {'forward_reads': 'R1.fastq.gz',
              'reverse_reads': 'R2.fastq.gz'}
