import luigi

from paip.task_types import CohortTask
from paip.pipeline import AnnotateWithVEP


class SplitMultisampleVCF(CohortTask):
    """
    Takes a multi-sample VCF and generates a new VCF for each sample in the
    cohort.
    """
    REQUIRES = AnnotateWithVEP

    def run(self):

        for sample, output_vcf in zip(self.sample_list, self.output()):
            with output_vcf.temporary_path() as self.temp_vcf:
                program_name = 'gatk SelectVariants sample'
                program_options = {
                    'input_vcf': self.input().fn,
                    'sample': sample,
                    'output_vcf': self.temp_vcf,
                }
                self.run_program(program_name, program_options)

            self.rename_temp_idx()

    def output(self):
        fn = self.cohort_path('{}.with_filters.vcf')
        vcfs = [fn.format(sample) for sample in self.sample_list]
        return [luigi.LocalTarget(vcf) for vcf in vcfs]

