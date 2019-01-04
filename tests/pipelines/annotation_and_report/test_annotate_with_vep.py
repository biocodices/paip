import pytest

from paip.pipelines.annotation_and_report import AnnotateWithVEP


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(AnnotateWithVEP)


def test_run(task):
    task.run()
    (command, ), kwargs = task.run_command.call_args

    assert 'vep' in command
    assert task.input().path in command
    assert '_summary.html' in command
    assert '.vep.tsv-luigi-tmp' in command
