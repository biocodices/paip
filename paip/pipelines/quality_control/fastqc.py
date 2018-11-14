from paip.task_types import SampleTask
from paip.pipelines.variant_calling import CheckFastqs, TrimAdapters
from paip.helpers.create_cohort_task import create_cohort_task


class FastQC(SampleTask):
    """
    Expects two raw read files and two trimmed read files of the same sample.
    Runs FastQC analysis on them, which produces HTML reports in the same dir.
    """
    REQUIRES = [CheckFastqs, TrimAdapters]
    OUTPUT = ['R1_fastqc.html', 'R1.trimmed_fastqc.html',
              'R2_fastqc.html', 'R2.trimmed_fastqc.html']

    def run(self):
        program_name = 'fastqc'

        # Run on raw reads (CheckFastqs output)
        raw_fastqs = self.input()[0]
        program_options = {
            'forward_reads': raw_fastqs[0].path,
            'reverse_reads': raw_fastqs[1].path,
        }
        self.run_program(program_name, program_options)

        # Run on trimmed reads (TrimAdapters output)
        trimmed_fastqs = self.input()[1]
        program_options = {
            'forward_reads': trimmed_fastqs[0].path,
            'reverse_reads': trimmed_fastqs[1].path,
        }
        self.run_program(program_name, program_options, log_append=True)


FastQCCohort = create_cohort_task(FastQC)

