import pytest

from paip.pipeline import AlignToReference, TrimAdapters


@pytest.fixture
def task(test_sample_task_params):
    return AlignToReference(**test_sample_task_params)


def test_requires(task):
    assert task.requires() == TrimAdapters(**task.param_kwargs)


def test_output(task, test_sample_path):
    expected_path = test_sample_path('Sample1.raw_alignment.sam')
    assert task.output().fn == expected_path

