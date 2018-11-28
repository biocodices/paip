from paip.task_types import SampleTask
from paip.pipelines.variant_calling import AlignToReferenceAndAddReadGroup
from paip.helpers.create_cohort_task import create_cohort_task


class SortCompressPutReadGroups(SampleTask):
    """
    Expects a SAM file with aligned reads. Reads sequencing data from the
    working directory and runs a command that adds (or replaces) read groups
    to each read. The result is written to a BAM file.
    """
    REQUIRES = AlignToReferenceAndAddReadGroup
    OUTPUT = 'raw_alignment.sorted.with_rg.bam'

    def run(self):
        with self.output().temporary_path() as self.temp_bam:
            program_name = 'picard AddOrReplaceReadGroups'
            program_options = {
                'input_sam': self.input().path,
                'output_bam': self.temp_bam,
            }

            self.run_program(program_name, program_options)

        self.rename_temp_bai()


SortCompressPutReadGroupsCohort = create_cohort_task(SortCompressPutReadGroups)
