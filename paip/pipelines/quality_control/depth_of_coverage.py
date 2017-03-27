from paip.pipelines.variant_calling import RecalibrateAlignmentScores
from paip.task_types import SampleTask
from paip.helpers.create_cohort_task import create_cohort_task


class DepthOfCoverage(SampleTask):
    """
    Takes a BAM and creates a file of coverage per base in the panel regions.
    """
    REQUIRES = RecalibrateAlignmentScores
    OUTPUT = 'depth_of_coverage'

    def run(self):
        with self.output().temporary_path() as outfile:
            program_name = 'gatk DepthOfCoverage'
            program_options = {
                'input_bam': self.input().fn,
                'outfile': outfile,
            }
            self.run_program(program_name, program_options)


            ### SEGUIR ACA ###
            # Deal with the depth_of_coverage accessory files!


DepthOfCoverageCohort = create_cohort_task(DepthOfCoverage)

