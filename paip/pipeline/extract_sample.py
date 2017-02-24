from os.path import join

import luigi

from paip.task_types import CohortTask
from paip.pipeline import AnnotateWithSnpeff


class ExtractSample(CohortTask):
    """
    Takes a multi-sample VCF and generates a new VCF of one specific sample
    passed as *sample* parameter.
    """
    sample = luigi.Parameter()

    def requires(self):
        params = self.param_kwargs.copy()
        del(params['sample'])  # 'sample' parameter is used only in this Task
        return AnnotateWithSnpeff(**params)

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
        fn = '{0}/{0}.with_filters.vcf'.format(self.sample)
        return luigi.LocalTarget(join(self.basedir, fn))

