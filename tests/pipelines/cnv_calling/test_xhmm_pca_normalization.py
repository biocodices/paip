import pytest

from paip.pipelines.cnv_calling import XhmmPCANormalization


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(XhmmPCANormalization)


def test_run(task, mock_rename):
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'xhmm --normalize' in command
    assert 'DATA.filtered_centered.RD.txt' in command
    assert 'DATA.RD_PCA' in command
    assert 'DATA.PCA_normalized.txt' in command

    mock_rename.assert_called_once
    assert 'luigi-tmp' in mock_rename.call_args[0][0]
    assert 'luigi-tmp' not in mock_rename.call_args[0][1]
