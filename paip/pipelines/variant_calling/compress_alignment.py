import os

from paip.task_types import SampleTask
from paip.pipelines.variant_calling import AlignToReference
from paip.helpers.create_cohort_task import create_cohort_task


class CompressAlignment(SampleTask):
    """
    Takes the .sam from the raw alignment and generates a .bam, then deletes
    the original .sam to save disk space.
    """
    REQUIRES = AlignToReference
    OUTPUT = 'raw_alignment.bam'

    def run(self):
        program_name = 'samtools SAM to BAM'
        program_options = {
            'input_sam': self.input().path,
        }

        with self.output().temporary_path() as temp_bam:
            self.run_program(program_name, program_options,
                            redirect_stdout_to_path=temp_bam)

        # Finally, we remove the SAM to save some disk space
        os.remove(self.input().path)


CompressAlignmentCohort = create_cohort_task(CompressAlignment)
