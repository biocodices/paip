import luigi

from paip.task_types import SampleTask
from paip.pipelines.variant_calling import ExternalExome
from paip.helpers.create_cohort_task import create_cohort_task


class FixContigNamesAndSampleName(SampleTask):
    """
    Take a VCF with contigs named "chr1", "chr2", ..., and make them just
    "1", "2", ..., so that we can use a reference FASTA with the latter
    contig names. Also, make sure the sample name in the VCF matches this
    task Sample's name, since we usually apply our own naming conventions to
    the samples.

    Meant to make Macrogen's VCF files compatible with our pipeline.
    """
    REQUIRES = ExternalExome

    def run(self):
        with self.output().temporary_path() as temp_out_vcf:
            program_name = 'fix contig names and sample name'
            program_options = {
                'input_vcf': self.input().path,
                'external_sample_name': self.external_sample_name,
                'new_sample_name': self.sample,
            }
            self.run_program(program_name, program_options,
                             redirect_stdout_to_path=temp_out_vcf)

    def output(self):
        path = self.input().path
        return luigi.LocalTarget(path.replace('.vcf', '.contigs_fix.vcf'))


FixContigNamesAndSampleNameCohort = \
    create_cohort_task(FixContigNamesAndSampleName)
