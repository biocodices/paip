from unittest.mock import MagicMock

import pytest

from paip.pipelines.cnv_calling.xhmm_pca import XhmmPCA, EmptyInputMatrix


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(XhmmPCA)


def test_check_matrix(task):
    # NOTE: Run this test before the next one, because the tested method
    # check_matrix() will be mocked in test_run().
    empty_matrix = pytest.helpers.file('empty_matrix.txt')

    with pytest.raises(EmptyInputMatrix):
        task.check_matrix(empty_matrix)


def test_run(task, mock_rename):
    check_matrix = MagicMock()

    task.check_matrix = check_matrix
    task.run()

    check_matrix.assert_called_once()

    (command, ), kwargs = task.run_command.call_args

    assert 'xhmm --PCA' in command
    assert 'DATA.filtered_centered.RD.txt' in command
    assert 'DATA-temp.RD_PCA' in command

    assert mock_rename.call_count == 3
    assert 'DATA-temp.RD_PCA' in mock_rename.call_args[0][0]
    assert 'DATA.RD_PCA' in mock_rename.call_args[0][1]

