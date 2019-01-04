import pytest

from paip.pipelines.quality_control import MultiQC


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(MultiQC)


def test_run(task, test_cohort_path):
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'multiqc' in command
    assert task.basedir in command
    assert task.output().path in command
