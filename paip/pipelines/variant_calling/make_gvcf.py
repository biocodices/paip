from paip.task_types import SampleTask
from paip.pipelines.variant_calling import RecalibrateAlignmentScores


class MakeGVCF(SampleTask):
    """
    Expects a BAM file. Runs GATK's HaplotypeCaller to produce a gVCF
    for the sample. It also outputs a BAM file with the realignment that
    HaplotypeCaller makes before calling the genotypes.
    """
    REQUIRES = RecalibrateAlignmentScores
    OUTPUT = ['g.vcf', 'hc_realignment.bam']

    def run(self):
        temp_vcf = self._find_output('.g.vcf').temporary_path
        temp_bam = self._find_output('.bam').temporary_path

        with temp_vcf() as self.temp_vcf, temp_bam() as self.temp_bam:
            program_name = 'gatk HaplotypeCaller'
            program_options = {
                'input_bam': self.input().fn,
                'output_gvcf': self.temp_vcf,
                'output_bam': self.temp_bam,
            }

            self.run_program(program_name, program_options)

        self.rename_temp_idx()
        self.rename_temp_bai()

