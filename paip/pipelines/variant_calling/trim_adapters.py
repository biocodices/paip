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
    OUTPUT = {'forward_reads': 'R1.trimmed.fastq.gz',
              'reverse_reads': 'R2.trimmed.fastq.gz'}

    def run(self):
        make_temp_fwd = self.output()['forward_reads'].temporary_path
        make_temp_rev = self.output()['reverse_reads'].temporary_path

        with make_temp_fwd() as temp_fwd_file, make_temp_rev() as temp_rev_file:
            program_name = self.trim_software
            program_options = {
                'forward_reads': self.input()['forward_reads'].path,
                'reverse_reads': self.input()['reverse_reads'].path,
                'forward_output': temp_fwd_file,
                'reverse_output': temp_rev_file,
            }

            self.run_program(program_name, program_options)


TrimAdaptersCohort = create_cohort_task(TrimAdapters)
