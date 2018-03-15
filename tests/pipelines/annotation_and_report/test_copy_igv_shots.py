import shutil
from unittest.mock import Mock

import pytest

from paip.pipelines.annotation_and_report import CopyIGVShots


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(CopyIGVShots,
                               extra_params={'min_reportable_category': 'PAT'})


def test_output(task):
    assert task.output().path.endswith('/report_Sample1/images/igv')


def test_run(task, mock_makedirs, monkeypatch):
    mock_copy2 = Mock(name='copy2')
    monkeypatch.setattr(shutil, 'copy2', mock_copy2)

    task.run()

    assert mock_copy2.call_count == 2
    first_call = mock_copy2.call_args_list[1]
    second_call = mock_copy2.call_args_list[0]

    assert first_call[0][0].endswith('/igv_snapshots_PAT/img1.png')
    assert second_call[0][0].endswith('/igv_snapshots_PAT/img2.png')

    dest_dir = '/report_Sample1/images/igv'
    assert first_call[0][1].endswith(dest_dir)
    assert second_call[0][1].endswith(dest_dir)

