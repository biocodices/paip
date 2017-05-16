from paip.task_types import CohortTask
from paip.pipelines.cnv_calling import FilterAndCenterMatrix, XhmmPCA


class XhmmPCANormalization(CohortTask):
    """
    Takes the PCA values and sustracts the main components to the
    filtered-centered read depth matrix to produce a 'PCA-normalized' matrix.
    """
    REQUIRES = [FilterAndCenterMatrix, XhmmPCA]
    OUTPUT = 'DATA.PCA_normalized.txt'
    SUBDIR = 'xhmm_run'

    def run(self):
        program_name = 'xhmm PCA_normalization'
        program_options = {
            'filtered_centered_matrix': self.input()[0][0].path,
            'pca_files_basename': 'DATA.RD_PCA',
            'outfile': self.output().path,
        }
        self.run_program(program_name, program_options)
