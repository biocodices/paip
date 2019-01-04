import pytest

from paip.pipelines.cnv_calling import FilterAndCenterMatrix


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(FilterAndCenterMatrix)


def test_run(task):
    task.run()
    (command, ), kwargs = task.run_command.call_args

    assert 'xhmm --matrix' in command
    assert 'DATA.RD.txt' in command
    assert 'DATA.filtered_centered.RD.txt' in command
    assert 'filtered_targets.txt' in command
    assert 'filtered_samples.txt' in command
    assert 'extreme_gc_targets.txt' in command
