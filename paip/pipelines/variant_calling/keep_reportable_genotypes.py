from paip.task_types import SampleTask
from paip.pipelines.variant_calling import ExtractSample


class KeepReportableGenotypes(SampleTask):
    """
    Takes a single-sample VCF with filters applied and generates a new VCF
    for that sample where only the variants with FILTER=PASS and genotypes
    with DP > min_dp and GQ > min_gq are kept.
    """
    OUTPUT = 'reportable.vcf'

    def requires(self):
        return ExtractSample(**self.param_kwargs)

    def run(self):
        with self.output().temporary_path() as self.temp_vcf:
            program_name = 'gatk SelectVariants reportable'
            program_options = {
                'input_vcf': self.input().path,
                'sample': self.sample,
                'min_GQ': self.min_gq,
                'min_DP': self.min_dp,
                'output_vcf': self.temp_vcf,
            }
            self.run_program(program_name, program_options)

        self.rename_temp_idx()

