import luigi

from paip.task_types import SampleTask
from paip.pipelines.variant_calling import (
    AlignToReferenceAndAddReadGroup,
    ValidateSam
)
from paip.helpers.create_cohort_task import create_cohort_task


class SortAndCompressAlignment(SampleTask):
    """
    Takes a SAM file and outputs a sorted BAM file.
    """
    REQUIRES = {
        'alignment': AlignToReferenceAndAddReadGroup,
        'validation': ValidateSam,
    }

    def run(self):
        with self.output().temporary_path() as temp_bam:
            program_name = 'picard SortSam'
            program_options = {
                'input_sam': self.input()['alignment'].path,
                'output_bam': temp_bam,
            }
            self.run_program(program_name, program_options)

        #  self.rename_temp_bai()

    def output(self):
        path = self.input()['alignment'].path.replace('.sam', '.sorted.bam')
        return luigi.LocalTarget(path)


SortAndCompressAlignmentCohort = create_cohort_task(SortAndCompressAlignment)
