from paip.task_types import CohortTask
from paip.pipelines.quality_control import DepthOfCoverageCohort


class MergeGATKDepths(CohortTask):
    """
    Takes the `.sample_interval_summary` sample files that are the result
    of GATK's DepthOfCoverage and merges the mean_coverage in a single matrix
    of sample vs. panel target.
    """
    REQUIRES = DepthOfCoverageCohort
    OUTPUT = 'DATA.RD.txt'
    SUBDIR = 'xhmm_run'

    def run(self):
        sample_cvg_files = ' '.join(
            ['--GATKdepths {}.sample_coverage_summary'.format(target.path)
             for target in self.requires().input()]
        )

        with self.output().temporary_path() as tempfile:
            program_name = 'xhmm MergeGATKDepths'
            program_options = {
                'sample_cvg_files': sample_cvg_files,
                'outfile': tempfile,
            }
            self.run_program(program_name, program_options)

