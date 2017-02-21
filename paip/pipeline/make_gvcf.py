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
        temp_gvcf = self.output()[0].temporary_path
        temp_idx = self.output()[1].temporary_path
        temp_bam = self.output()[2].temporary_path

        with temp_gvcf() as self.temp_gvcf, temp_idx(), temp_bam() as self.temp_bam:

            # Pipeline type might be "all_sites" or "variant_sites" here:
            program_name = 'gatk HaplotypeCaller ' + self.pipeline_type

            program_options = {
                'input_bam': self.input().fn,
                'output_gvcf': self.temp_gvcf,
                'output_bam': self.temp_bam,
            }

            self.run_program(program_name, program_options)

    def output(self):
        gvcf_fn = self.sample_path('g.vcf')
        idx_fn = gvcf_fn + '.idx'
        bam_fn = self.sample_path(self.pipeline_type + '_realignment.bam')
        return [luigi.LocalTarget(fn) for fn in [gvcf_fn, idx_fn, bam_fn]]

