import luigi

from paip.task_types import SampleTask
from paip.pipelines.variant_calling import ExternalExome
from paip.helpers.create_cohort_task import create_cohort_task


class FixContigNames(SampleTask):
    """
    Take a VCF with contigs named "chr1", "chr2", ..., and make them just
    "1", "2", ..., so that we can use a reference FASTA with the latter
    contig names.

    Meant to make Macrogen's VCF files compatible with our pipeline.
    """
    REQUIRES = ExternalExome

    def run(self):
        with self.output().temporary_path() as temp_out_vcf:
            program_name = 'fix contig names'
            program_options = {
                'input_vcf': self.input().path,
            }
            self.run_program(program_name, program_options,
                             redirect_stdout_to_path=temp_out_vcf)

    def output(self):
        path = self.input().path
        return luigi.LocalTarget(path.replace('.vcf', '.contigs_fix.vcf'))


FixContigNamesCohort = create_cohort_task(FixContigNames)
