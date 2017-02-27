import luigi

from paip.task_types import CohortTask
from paip.variant_calling import FilterGenotypes


class SplitMultisampleVCF(CohortTask):
    """
    Takes a multi-sample VCF and generates a new VCF for each sample in the
    cohort. Applies ExtractSample to all samples of the cohort.
    """
    def requires(self):
        for sample in self.sample_list:
            yield ExtractSample(sample=sample, **self.param_kwargs)

    def output(self):
        return [require.output() for require in self.requires()]


class ExtractSample(CohortTask):
    """
    Takes a multi-sample VCF and generates a new VCF of keeping the
    genotypes of one *sample*.
    """
    sample = luigi.Parameter()

    def requires(self):
        params = self.param_kwargs.copy()
        del(params['sample'])  # 'sample' parameter is used only in this Task
        return FilterGenotypes(**params)

    def run(self):
        with self.output().temporary_path() as self.temp_vcf:
            program_name = 'gatk SelectVariants sample'
            program_options = {
                'input_vcf': self.input().fn,
                'sample': self.sample,
                'output_vcf': self.temp_vcf,
            }
            self.run_program(program_name, program_options)

        self.rename_temp_idx()

    def output(self):
        return luigi.LocalTarget(self.sample_path('with_filters.vcf'))

