import pytest

from paip.pipelines.cnv_calling import DiscoverCNVs


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(DiscoverCNVs)


def test_run(task):
    task.run()
    (command, ), kwargs = task.run_command.call_args

    assert 'xhmm --discover' in command
    assert 'Cohort1.DATA' in command
    assert 'DATA.PCA_normalized.filtered.sample_zscores.RD.txt' in command
    assert 'DATA.same_filtered.RD.txt' in command
    assert 'DATA.xcnv' in command
    assert 'DATA.aux_xcnv' in command
