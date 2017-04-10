from paip.task_types import CohortTask
from paip.pipelines.cnv_calling import MergeGATKDepths, GCContentByInterval


class FilterAndCenterMatrix(CohortTask):
    """
    Takes the panel BED file and calculates the GC content by interval using
    GATK's GCContentByInterval module.
    """
    REQUIRES = [MergeGATKDepths, GCContentByInterval]
    OUTPUT = ['DATA.filtered_centered.RD.txt',
              'DATA.filtered_centered.RD.txt.filtered_targets.txt',
              'DATA.filtered_centered.RD.txt.filtered_samples.txt']
    SUBDIR = 'xhmm_run'

    def run(self):
        program_name = 'xhmm centerData'
        program_options = {
            'read_depth_matrix': self.input()[0].path,
            'out_matrix': self.output()[0].path,
            'out_excluded_targets': self.output()[1].path,
            'out_excluded_samples': self.output()[2].path,
            'extreme_gc_targets': self.input()[1][1].path,
            # ^ 2nd output of GCContentByInterval
        }
        self.run_program(program_name, program_options)

