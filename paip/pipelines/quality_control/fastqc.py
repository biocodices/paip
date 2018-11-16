from paip.task_types import SampleTask
from paip.pipelines.variant_calling import CheckFastqs, TrimAdapters
from paip.helpers.create_cohort_task import create_cohort_task


class FastQC(SampleTask):
    """
    Expects two raw read files and two trimmed read files of the same sample.
    Runs FastQC analysis on both types, produces HTML reports in the same dir.
    """
    REQUIRES = {'raw_reads': CheckFastqs, 'trimmed_reads': TrimAdapters}
    OUTPUT = ['R1_fastqc.html', 'R1.trimmed_fastqc.html',
              'R2_fastqc.html', 'R2.trimmed_fastqc.html']

    def run(self):
        program_name = 'fastqc'

        program_options = {
            'forward_reads': self.input()['raw_reads']['forward_reads'].path,
            'reverse_reads': self.input()['raw_reads']['reverse_reads'].path,
        }
        self.run_program(program_name, program_options)

        program_options = {
            'forward_reads': self.input()['trimmed_reads']['forward_reads'].path,
            'reverse_reads': self.input()['trimmed_reads']['reverse_reads'].path,
        }
        self.run_program(program_name, program_options, log_append=True)


FastQCCohort = create_cohort_task(FastQC)
