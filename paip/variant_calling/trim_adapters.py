from paip.task_types import SampleTask
from paip.variant_calling import CheckFastqs
from paip.helpers.create_cohort_task import create_cohort_task


class TrimAdapters(SampleTask):
    """
    Expects fastq files with forward and reverse reads of the same
    sample. Trims the adapters of those reads files and generates
    new fastq files.
    """
    REQUIRES = CheckFastqs

    def run(self):
        program_name = 'fastq-mcf'
        program_options = {
            'forward_reads': self.input()[0].fn,
            'reverse_reads': self.input()[1].fn,
            'forward_output': self.output()[0].fn,
            'reverse_output': self.output()[1].fn,
        }

        self.run_program(program_name, program_options)

    OUTPUT = ['R1.trimmed_reads.fastq', 'R2.trimmed_reads.fastq']


TrimAdaptersCohort = create_cohort_task(TrimAdapters)

