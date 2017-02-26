import luigi

from paip.task_types import CohortTask
from paip.variant_calling import ExtractSample


class KeepReportableGenotypes(CohortTask):
    """
    Wrapper task, applies KeepSampleReportableGenotypes for all samples of the
    cohort.
    """
    min_gq = luigi.IntParameter(default=30)
    min_dp = luigi.IntParameter(default=30)

    def requires(self):
        for sample in self.sample_list:
            yield KeepSampleReportableGenotypes(sample=sample,
                                                **self.param_kwargs)

    def output(self):
        return [require.output() for require in self.requires()]


class KeepSampleReportableGenotypes(CohortTask):
    """
    Takes a single-sample VCF with filters applied and generates a new VCF
    for that sample where only the variants with FILTER=PASS and genotypes
    with DP > min_dp and GQ > min_gq are kept.
    """
    sample = luigi.Parameter()
    min_gq = luigi.IntParameter()
    min_dp = luigi.IntParameter()

    def requires(self):
        params = self.param_kwargs.copy()
        # threshold parameters are not used upstream in the pipeline:
        del(params['min_gq'])
        del(params['min_dp'])
        return ExtractSample(**params)

    def run(self):
        with self.output().temporary_path() as self.temp_vcf:
            program_name = 'gatk SelectVariants reportable'
            program_options = {
                'input_vcf': self.input().fn,
                'sample': self.sample,
                'min_GQ': self.min_gq,
                'min_DP': self.min_dp,
                'output_vcf': self.temp_vcf,
            }
            self.run_program(program_name, program_options)

        self.rename_temp_idx()

    def output(self):
        return luigi.LocalTarget(self.sample_path('reportable.vcf'))

