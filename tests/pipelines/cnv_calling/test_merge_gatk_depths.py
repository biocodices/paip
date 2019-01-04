import pytest

from paip.pipelines.cnv_calling import MergeGATKDepths


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(MergeGATKDepths)


def test_run(task):
    task.run()
    (command, ), kwargs = task.run_command.call_args

    assert 'xhmm --mergeGATKdepths' in command
    assert 'DATA.RD.txt' in command

    cvg_files = ['Sample1.depth_of_coverage.sample_interval_summary',
                 'Sample2.depth_of_coverage.sample_interval_summary']

    for cvg_file in cvg_files:
        assert cvg_file in command
