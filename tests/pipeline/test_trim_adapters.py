import pytest

from paip.pipeline import TrimAdapters, CheckFastqs


@pytest.fixture
def task(test_sample_task_params):
    return TrimAdapters(**test_sample_task_params)


def test_requires(task):
    assert task.requires() == CheckFastqs(**task.param_kwargs)


def test_output(task, test_sample_path):
    expected_paths = [test_sample_path('Sample1.R1.trimmed_reads.fastq'),
                      test_sample_path('Sample1.R2.trimmed_reads.fastq')]
    assert [out.fn for out in task.output()] == expected_paths

