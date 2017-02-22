import pytest

from paip.pipeline import FilterIndels


@pytest.fixture
def task(test_cohort_task_params):
    return FilterIndels(**test_cohort_task_params)


def test_output(task, test_cohort_path):
    fn = 'Cohort1__2_Samples.variant_sites.dbsnp.indels.filt.vcf'
    expected_path = test_cohort_path(fn)
    assert task.output().fn == expected_path

