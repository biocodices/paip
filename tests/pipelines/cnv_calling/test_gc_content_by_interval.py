import pytest

from paip.pipelines.cnv_calling import GCContentByInterval


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(GCContentByInterval)


def test_run(task):
    task.run()

    (command, ), kwargs = task.run_command.call_args_list[0]
    assert 'GenomeAnalysisTK.jar -T GCContentByInterval' in command
    assert 'Cohort1.DATA.locus_GC.txt' in command

    (command, ), kwargs = task.run_command.call_args_list[1]
    assert 'awk' in command
    assert 'Cohort1.extreme_gc_targets.txt' in command
