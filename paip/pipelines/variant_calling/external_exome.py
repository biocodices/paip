from paip.task_types import SampleTask
from paip.helpers.create_cohort_task import create_cohort_task


class ExternalExome(SampleTask):
    """
    Check that exome VCF files are present for the sample.
    """
    OUTPUT = 'external_exome.vcf'
    # TODO: This should be an external task like CheckFastqs


ExternalExomeCohort = create_cohort_task(ExternalExome)
