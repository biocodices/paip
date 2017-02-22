import pytest

from paip.pipeline import CheckFastqs


@pytest.fixture
def task(test_sample_task_params):
    return CheckFastqs(**test_sample_task_params)


def test_output(task, test_sample_path):
    expected_paths = [test_sample_path('Sample1.R1.fastq'),
                      test_sample_path('Sample1.R2.fastq')]
    assert [out.fn for out in task.output()] == expected_paths

