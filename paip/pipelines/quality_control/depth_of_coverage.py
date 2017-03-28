import os

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
        with self.output().temporary_path() as tempfile:
            program_name = 'gatk DepthOfCoverage'
            program_options = {
                'input_bam': self.input().fn,
                'outfile': tempfile,
            }
            self.run_program(program_name, program_options)

        # A whole bunch of extra files are created using the original
        # output filename as a base:
        extra_files = [
            '.sample_cumulative_coverage_counts',
            '.sample_cumulative_coverage_proportions',
            '.sample_interval_statistics',
            '.sample_interval_summary',
            '.sample_statistics',
            '.sample_summary',
        ]

        for extra_extension in extra_files:
            temp_filename = tempfile + extra_extension
            intended_filename = self.output().fn + extra_extension
            os.rename(temp_filename, intended_filename)


DepthOfCoverageCohort = create_cohort_task(DepthOfCoverage)

