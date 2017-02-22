import luigi

from paip.task_types import SampleTask
from paip.pipeline import RecalibrateAlignmentScores


class MakeGVCF(SampleTask):
    """
    Expects a BAM file. Runs GATK's HaplotypeCaller to produce a gVCF
    for the sample. It also outputs a BAM file with the realignment that
    HaplotypeCaller makes before calling the genotypes.
    """
    pipeline_type = luigi.Parameter()

    def requires(self):
        return RecalibrateAlignmentScores(sample=self.sample)

    def run(self):
        temp_vcf = self._find_output('.g.vcf').temporary_path
        temp_bam = self._find_output('.bam').temporary_path

        with temp_vcf() as self.temp_vcf, temp_bam() as self.temp_bam:

            # Pipeline type might be "all_sites" or "variant_sites" here:
            program_name = 'gatk HaplotypeCaller ' + self.pipeline_type
            program_options = {
                'input_bam': self.input().fn,
                'output_gvcf': self.temp_vcf,
                'output_bam': self.temp_bam,
            }

            self.run_program(program_name, program_options)

        self.rename_temp_idx()
        self.rename_temp_bai()

    def output(self):
        vcf_fn = self.sample_path('g.vcf')
        bam_fn = self.sample_path(self.pipeline_type + '_realignment.bam')
        return [luigi.LocalTarget(fn) for fn in [vcf_fn, bam_fn]]

