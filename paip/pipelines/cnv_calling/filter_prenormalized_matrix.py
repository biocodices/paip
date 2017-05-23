from paip.task_types import CohortTask
from paip.pipelines.cnv_calling import (
    MergeGATKDepths,
    FilterAndCenterMatrix,
    XhmmZscores
)


class FilterPrenormalizedMatrix(CohortTask):
    """
    Filters the original read depth matrix removing the targets and samples
    that were excluded during the Z-scores step.
    """
    REQUIRES = [MergeGATKDepths, FilterAndCenterMatrix, XhmmZscores]
    OUTPUT = 'DATA.same_filtered.RD.txt'
    SUBDIR = 'xhmm_run'

    def run(self):
        with self.output().temporary_path() as temp_outfile:
            program_name = 'xhmm filter_prenormalized_matrix'
            program_options = {
                # Original raw read depths:
                'read_depth_matrix': self.input()[0].path,

                # First filtering files:
                'raw_excluded_targets': self.input()[1][1].path,
                'raw_excluded_samples': self.input()[1][2].path,

                # Z-score based filtering files:
                'zscore_excluded_targets': self.input()[2][1].path,
                'zscore_excluded_samples': self.input()[2][2].path,

                'outfile': temp_outfile,
            }
            self.run_program(program_name, program_options)

