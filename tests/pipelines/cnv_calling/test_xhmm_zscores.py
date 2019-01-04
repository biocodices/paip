import pytest

from paip.pipelines.cnv_calling import XhmmZscores


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(XhmmZscores)


def test_run(task):
    task.run()
    (command, ), kwargs = task.run_command.call_args

    assert 'xhmm --matrix' in command
    assert 'DATA.PCA_normalized.txt' in command
    assert 'DATA.PCA_normalized.filtered.sample_zscores.RD.txt' in command
    assert 'filtered_targets.txt' in command
    assert 'filtered_samples.txt' in command
