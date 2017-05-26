from paip.task_types import CohortTask
from paip.pipelines.cnv_calling import XhmmPCANormalization


class XhmmZscores(CohortTask):
    """
    Takes the 'PCA-normalized' read depth matrix and produces a matrix of
    z-scores values of it (mean=0, sd=1).
    """
    REQUIRES = XhmmPCANormalization
    OUTPUT = [
        'DATA.PCA_normalized.filtered.sample_zscores.RD.txt',
        'DATA.PCA_normalized.filtered.sample_zscores.RD.txt.filtered_targets.txt',
        'DATA.PCA_normalized.filtered.sample_zscores.RD.txt.filtered_samples.txt'
    ]
    SUBDIR = 'xhmm_run'

    def run(self):
        with self.output()[0].temporary_path() as temp_zscores, \
             self.output()[1].temporary_path() as temp_targets, \
             self.output()[2].temporary_path() as temp_samples:

            program_name = 'xhmm Z_scores'
            program_options = {
                'pca_normalized_matrix': self.input()[0].path,
                'out_zscores': temp_zscores,
                'out_excluded_targets': temp_targets,
                'out_excluded_samples': temp_samples,
            }
            self.run_program(program_name, program_options)

