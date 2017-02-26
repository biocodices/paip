import pytest

from paip.variant_calling import MergeVCFs, CallTargets


@pytest.fixture
def task(test_cohort_task_params):
    test_cohort_task_params['pipeline_type'] = 'target_sites'
    return MergeVCFs(**test_cohort_task_params)


def test_requires(task):
    expected_dependencies = [
        CallTargets(sample='Sample1', basedir=task.basedir),
        CallTargets(sample='Sample2', basedir=task.basedir)
    ]
    assert task.requires() == expected_dependencies


@pytest.mark.skip(reason='Implement this')
def test_run(task, test_sample_path):
    assert 0

