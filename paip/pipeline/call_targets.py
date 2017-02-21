import luigi

from paip.task_types import SampleTask
from paip.pipeline import RecalibrateAlignmentScores


class CallTargets(SampleTask):
    """
    Expects a BAM file. Runs GATK's HaplotypeCaller to call the genotypes
    of the variants specified in a panel_variants VCF.
    """
    pipeline_type = luigi.Parameter()

    def requires(self):
        return RecalibrateAlignmentScores(sample=self.sample)

    def run(self):
        assert self.pipeline_type == 'target_sites'  # Safety check

        output_vcf = self.output()[0]
        temp_vcf = output_vcf.temporary_path

        # This is a workaround to have Luigi rename the temporary files
        # .idx, .bam, .bai while not adding these extra files to the Task's
        # output, which would make downstream processing more convoluted:
        output_idx = output_vcf.fn + '.idx'
        output_bam = self.sample_path('target_sites_realignment.bam')
        output_bai = output_bam + '.bai'

        temp_idx = luigi.LocalTraget(output_idx).temporary_path
        temp_bam = luigi.LocalTarget(output_bam).temporary_path
        temp_bai = luigi.LocalTarget(output_bai).temporary_path

        with temp_vcf() as self.temp_vcf, temp_idx(), \
             temp_bam() as self.temp_bam, temp_bai():

            program_name = 'gatk HaplotypeCaller ' + self.pipeline_type
            program_options = {
                'input_bam': self.input().fn,
                'output_vcf': self.temp_vcf,
                'output_bam': self.temp_bam,
            }

            self.run_program(program_name, program_options)

    def output(self):
        fn = self.sample_path('raw_targets.vcf')
        return luigi.LocalTarget(fn)

