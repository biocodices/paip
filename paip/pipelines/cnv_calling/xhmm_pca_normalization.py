import os

from paip.task_types import CohortTask
from paip.pipelines.cnv_calling import FilterAndCenterMatrix, XhmmPCA


class XhmmPCANormalization(CohortTask):
    """
    Takes the PCA values and sustracts the main components to the
    filtered-centered read depth matrix to produce a 'PCA-normalized' matrix.
    """
    REQUIRES = [FilterAndCenterMatrix, XhmmPCA]
    OUTPUT = ['DATA.PCA_normalized.txt',
              'DATA.PCA_normalized.txt.num_removed_PC.txt']
    SUBDIR = 'xhmm_run'

    def run(self):
        with self.output()[0].temporary_path() as temp_outfile:
            program_name = 'xhmm PCA_normalization'
            program_options = {
                'filtered_centered_matrix': self.input()[0][0].path,
                'pca_files_basename': self.path('DATA.RD_PCA'),
                'outfile': temp_outfile,
            }
            self.run_program(program_name, program_options)

        # The second output file must be manually renamed, since it has a
        # suffix added by XHMM to the luigi-generated temporary path:
        generated_file = temp_outfile + '.num_removed_PC.txt'
        intended_file = self.output()[1].path
        os.rename(generated_file, intended_file)

