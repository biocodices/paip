import luigi

from paip.task_types import CohortTask
from paip.pipeline import JointGenotyping


class AnnotateWithDbSNP(CohortTask):
    """
    Take a cohort VCF and add IDs from a dbSNP VCF file.

    This step compensates the fact that, while GATK's HaplotypeCaller
    does annotate the IDs of *variant* sites, it does not annotate
    IDs of homREF sites.
    """
    def requires(self):
        return JointGenotyping(basedir=self.basedir, samples=self.samples)

    def run(self):

        with self.output().temporary_path() as self.temp_output_path:
            program_name = 'snpsift dbSNP'
            program_options = {
                'input_vcf': self.input().fn,
            }

            stdout, _ = self.run_program(program_name, program_options,
                                         log_stdout=False)

            with open(self.temp_output_path, 'wb') as f:
                f.write(stdout)

    def output(self):
        fn = 'all_sites.raw_genotypes.dbsnp.vcf'
        return luigi.LocalTarget(self.cohort_path(fn))

