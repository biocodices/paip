import pytest

from paip.pipelines.cnv_calling import FilterPrenormalizedMatrix


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(FilterPrenormalizedMatrix)


def test_run(task):
    task.run()
    (command, ), kwargs = task.run_command.call_args

    assert 'xhmm --matrix' in command
    assert 'DATA.RD.txt' in command
    assert 'DATA.filtered_centered.RD.txt.filtered_targets.txt' in command
    assert 'DATA.PCA_normalized.filtered.sample_zscores.RD.txt.filtered_targets.txt' in command
    assert 'DATA.filtered_centered.RD.txt.filtered_samples.txt' in command
    assert 'DATA.PCA_normalized.filtered.sample_zscores.RD.txt.filtered_samples.txt' in command
    assert 'DATA.same_filtered.RD.txt' in command
