import pytest

from paip.pipeline import MergeVCFs, CallTargets


@pytest.fixture
def task(test_cohort_task_params):
    test_cohort_task_params['pipeline_type'] = 'target_sites'
    return MergeVCFs(**test_cohort_task_params)


def test_requires(task):
    expected_dependencies = [CallTargets(sample='Sample1'),
                             CallTargets(sample='Sample2')]
    assert task.requires() == expected_dependencies


def test_output(task, test_cohort_path):
    expected = test_cohort_path('Cohort1__2_Samples.target_sites.vcf')
    assert task.output().fn == expected

