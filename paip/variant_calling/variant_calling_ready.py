import luigi

from paip.task_types import SampleTask


class VariantCallingReady(luigi.ExternalTask, SampleTask):
    """
    Checks the complete variant calling is done.
    """
    pipeline_type = luigi.Parameter()

    def output(self):
        fp = self.sample_path('{}.reportable.vcf'.format(self.pipeline_type))
        return luigi.LocalTarget(fp)

