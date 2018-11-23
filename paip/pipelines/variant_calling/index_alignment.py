from paip.task_types import SampleTask
from paip.pipelines.variant_calling import MarkDuplicates
from paip.helpers.create_cohort_task import create_cohort_task


class IndexAlignment(SampleTask):
    """
    Takes a BAM and creates its BAI (index) companion.
    """
    REQUIRES = MarkDuplicates
    OUTPUT = "deduped_alignment.sorted.with_rg.bai"

    def run(self):
        with self.output().temporary_path() as temp_bai:
            program_name = 'picard BuildBamIndex'
            program_options = {
                'input_bam': self.input()['deduped_bam'].path,
            }
            self.run_program(program_name, program_options)


IndexAlignmentCohort = create_cohort_task(IndexAlignment)
