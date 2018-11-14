from paip.task_types import CohortTask
from paip.pipelines.cnv_calling import (
    XhmmZscores,
    DiscoverCNVs,
    FilterPrenormalizedMatrix,
)


class GenotypeCNVs(CohortTask):
    """
    Takes the CNVs discovered by DiscoverCNVs and the normalized read depths
    of each sample and locus, and calls genotypes for each sample at each CNV.

    Generates a VCF with the results.
    """
    REQUIRES = [XhmmZscores, FilterPrenormalizedMatrix, DiscoverCNVs]
    SUBDIR = 'xhmm_run'
    OUTPUT = 'DATA.vcf'

    def run(self):
        program_name = 'xhmm genotype'
        program_options = {
            # XhmmZscores first output
            'zscores_matrix': self.input()[0][0].path,

            # FilterPrenormalizedMatrix only output
            'read_depth_matrix': self.input()[1].path,

            # DiscoverCNVs first output
            'cnvs_file': self.input()[2][0].path,

            'output_vcf': self.output().path,
        }

        self.run_program(program_name, program_options)

