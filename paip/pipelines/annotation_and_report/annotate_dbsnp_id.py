import luigi

from paip.task_types import SampleTask
from paip.pipelines.ion_torrent import TorrentVariantCaller
from paip.helpers.create_cohort_task import create_cohort_task


class AnnotateDbsnpId(SampleTask):
    """
    Take a sample VCF and add IDs from a dbSNP VCF file. Replace any previous
    ID in the VCF, leaving only the preferred DbSNP's version.
    """
    REQUIRES = TorrentVariantCaller

    def run(self):
        with self.output().temporary_path() as temp_vcf:
            program_name = 'snpsift dbSNP'
            program_options = {
                'input_vcf': self.input()['gzipped_vcf'].path,
            }
            self.run_program(program_name, program_options,
                             redirect_stdout_to_path=temp_vcf,
                             log_stdout=False)

    def output(self):
        fn = self.input()['gzipped_vcf'].path.replace('.vcf', '.dbSNP.vcf')
        return luigi.LocalTarget(fn)


AnnotateDbsnpIdCohort = create_cohort_task(AnnotateDbsnpId)
