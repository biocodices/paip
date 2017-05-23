from paip.task_types import CohortTask
from paip.pipelines.cnv_calling import FilterPrenormalizedMatrix, XhmmZscores


class DiscoverCNVs(CohortTask):
    """
    Takes the filtered read depth matrix and the z-scores matrix and runs
    XHMM to discover CNVs in the samples.
    """
    REQUIRES = [FilterPrenormalizedMatrix, XhmmZscores]
    OUTPUT = ['DATA.xcnv', 'DATA.aux_xcnv']
    SUBDIR = 'xhmm_run'

    def run(self):
        with self.output()[0].temporary_path() as temp_xcnv, \
             self.output()[1].temporary_path() as temp_aux:

            program_name = 'xhmm discover'
            program_options = {
                'data_files_basename': self.path('DATA'),
                'zscores_matrix': self.input()[1][0].path,
                'read_depth_matrix_filtered': self.input()[0].path,
                'outfile': temp_xcnv,
                'aux_outfile': temp_aux,
            }
            self.run_program(program_name, program_options)

