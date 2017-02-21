import luigi

from paip.task_types import SampleTask
from paip.pipeline import CheckFastqs


class TrimAdapters(SampleTask):
    """
    Expects fastq files with forward and reverse reads of the same
    sample. Trims the adapters of those reads files and generates
    new fastq files.
    """
    def requires(self):
        return CheckFastqs(sample=self.sample)

    def run(self):
        options = {
            'forward_reads': self.input()[0].fn,
            'reverse_reads': self.input()[1].fn,
            'forward_output': self.output()[0].fn,
            'reverse_output': self.output()[1].fn,
        }

        self.run_program('fastq-mcf', options)

    def output(self):
        trimmed_fastqs = self.sample_paths(['R1.trimmed_reads.fastq',
                                            'R2.trimmed_reads.fastq'])
        return [luigi.LocalTarget(fn) for fn in trimmed_fastqs]

