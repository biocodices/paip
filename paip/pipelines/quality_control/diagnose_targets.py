from paip.pipelines.variant_calling import RecalibrateAlignmentScores
from paip.task_types import SampleTask
from paip.helpers.create_cohort_task import create_cohort_task


class DiagnoseTargets(SampleTask):
    """
    Takes a BAM and the panel's BED and creates a VCF of coverage stats per
    region.
    """
    REQUIRES = RecalibrateAlignmentScores
    OUTPUT = 'coverage_diagnosis.vcf'

    def run(self):
        with self.output().temporary_path() as self.temp_vcf:
            program_name = 'gatk DiagnoseTargets'
            program_options = {
                'input_bam': self.input().path,
                'min_dp': self.min_dp,
                'output_vcf': self.temp_vcf,
            }
            self.run_program(program_name, program_options)

        self.rename_temp_idx()


DiagnoseTargetsCohort = create_cohort_task(DiagnoseTargets)
