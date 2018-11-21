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
        program_name = self.trim_software
        program_options = {
            'forward_reads': self.input()['forward_reads'].path,
            'reverse_reads': self.input()['reverse_reads'].path,

            # NOTE: we can't use luigi's helpful temporary paths for this task
            # because cutadapt expects filenames ending with ".gz" if you
            # want to compress the output, and luigi's temporary paths end with
            # "-luigi-<some_number>"
            'forward_output': self.output()['forward_reads'].path,
            'reverse_output': self.output()['reverse_reads'].path,
        }

        self.run_program(program_name, program_options)


TrimAdaptersCohort = create_cohort_task(TrimAdapters)
