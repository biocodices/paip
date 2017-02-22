import pytest

from paip.pipeline import FilterSNPs


@pytest.fixture
def task(test_cohort_task_params):
    return FilterSNPs(**test_cohort_task_params)


def test_output(task, test_cohort_path):
    fn = 'Cohort1__2_Samples.variant_sites.dbsnp.snps.filt.vcf'
    expected_path = test_cohort_path(fn)
    assert task.output().fn == expected_path


