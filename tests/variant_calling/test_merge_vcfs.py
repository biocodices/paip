import pytest

from paip.variant_calling import MergeVCFs, ResetFilters


@pytest.fixture
def task(cohort_task_params):
    cohort_task_params['pipeline_type'] = 'target_sites'
    return MergeVCFs(**cohort_task_params)


def test_requires(task):
    expected_dependencies = [
        ResetFilters(sample='Sample1', **task.param_kwargs),
        ResetFilters(sample='Sample2', **task.param_kwargs)
    ]
    assert task.requires() == expected_dependencies


@pytest.mark.skip(reason='Implement this')
def test_run(task, test_sample_path):
    assert 0

