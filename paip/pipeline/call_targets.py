import luigi

from paip.task_types import SampleTask
from paip.pipeline import RecalibrateAlignmentScores


class CallTargets(SampleTask):
    """
    Expects a BAM file. Runs GATK's HaplotypeCaller to call the genotypes
    of the variants specified in a panel_variants VCF.
    """
    def requires(self):
        return RecalibrateAlignmentScores(sample=self.sample)

    def run(self):
        temp_vcf = self._find_output('.vcf').temporary_path
        temp_bam = self._find_output('.bam').temporary_path

        with temp_vcf() as self.temp_vcf, temp_bam() as self.temp_bam:

            program_name = 'gatk HaplotypeCaller target_sites'
            program_options = {
                'input_bam': self.input().fn,
                'output_vcf': self.temp_vcf,
                'output_bam': self.temp_bam,
            }

            self.run_program(program_name, program_options)

        self.rename_temp_idx()
        self.rename_temp_bai()

    def output(self):
        vcf_fn = self.sample_path('vcf')
        bam_fn = self.sample_path('target_sites_realignment.bam')
        return [luigi.LocalTarget(fn) for fn in [vcf_fn, bam_fn]]

