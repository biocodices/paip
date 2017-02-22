import pytest

from paip.pipeline import AddOrReplaceReadGroups, AlignToReference


@pytest.fixture
def task(test_sample_task_params):
    return AddOrReplaceReadGroups(**test_sample_task_params)


def test_requires(task):
    assert task.requires() == AlignToReference(**task.param_kwargs)


def test_output(task, test_sample_path):
    expected_path = test_sample_path('Sample1.raw_alignment_with_read_groups.bam')
    assert task.output().fn == expected_path

