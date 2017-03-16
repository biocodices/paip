from paip.pipelines.variant_calling import RecalibrateAlignmentScores
from paip.task_types import SampleTask


class DiagnoseTargets(SampleTask):
    """
    Takes a BAM and the panel's BED and creates a VCF of coverage stats per
    region.
    """
    REQUIRES = RecalibrateAlignmentScores
    OUTPUT = 'coverage_diagnosis.vcf'

    def run(self):
        with self.output().temporary_path() as temp_outfile:
            program_name = 'gatk DiagnoseTargets'
            program_options = {
                'input_bam': self.input().fn,
                'output_vcf': temp_outfile,
            }
            self.run_program(program_name, program_options)

        self.rename_temp_idx()

