from paip.task_types import SampleTask
from paip.pipelines.variant_calling import CheckFastqs
from paip.helpers.create_cohort_task import create_cohort_task


class TrimAdapters(SampleTask):
    """
    Expects fastq files with forward and reverse reads of the same
    sample. Trims the adapters of those reads files and generates
    new fastq files.
    """
    REQUIRES = CheckFastqs
    OUTPUT = ['R1.trimmed.fastq', 'R2.trimmed.fastq']

    def run(self):
        temp_R1 = self.output()[0].temporary_path
        temp_R2 = self.output()[1].temporary_path

        with temp_R1() as temp_R1_file, temp_R2() as temp_R2_file:
            program_name = self.trim_software
            program_options = {
                'forward_reads': self.input()[0].path,
                'reverse_reads': self.input()[1].path,
                'forward_output': temp_R1_file,
                'reverse_output': temp_R2_file,
            }

            self.run_program(program_name, program_options)


TrimAdaptersCohort = create_cohort_task(TrimAdapters)

