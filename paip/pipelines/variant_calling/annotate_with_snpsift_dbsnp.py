import luigi

from paip.task_types import CohortTask
from paip.pipelines.variant_calling import JointGenotyping, MergeVCFs


class AnnotateWithSnpsiftDbSNP(CohortTask):
    """
    Take a cohort VCF and add IDs from a dbSNP VCF file.

    This step compensates the fact that, while GATK's HaplotypeCaller
    does annotate the IDs of *variant* sites, it does not annotate
    IDs of homREF sites.
    """
    def requires(self):
        in_targets_pipeline = self.pipeline_type == 'target_sites'
        dependency = MergeVCFs if in_targets_pipeline else JointGenotyping
        return dependency(**self.param_kwargs)

    def run(self):
        with self.output().temporary_path() as self.temp_vcf:
            program_name = 'snpsift dbSNP'
            program_options = {
                'input_vcf': self.input().path,
            }

            # Snpsift outputs the annotated VCF to STDOUT
            stdout, _ = self.run_program(program_name, program_options,
                                         log_stdout=False)

            with open(self.temp_vcf, 'wb') as f:
                f.write(stdout)

    def output(self):
        fn = self.input().path.replace('.vcf', '.snpsift_dbsnp.vcf')
        return luigi.LocalTarget(fn)

