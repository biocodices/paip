import luigi

from paip.task_types import SampleTask
from paip.pipelines.variant_calling import KeepReportableGenotypes
from paip.helpers.create_cohort_task import create_cohort_task


class VariantCallingReady(SampleTask, luigi.WrapperTask):
    """
    Dummy task to check if either the reportable VCF file for a sample is
    ready, whether it came from an external exome or a local pipeline.
    """
    REQUIRES = KeepReportableGenotypes

    def output(self):
        return self.input()


VariantCallingReadyCohort = create_cohort_task(VariantCallingReady)
