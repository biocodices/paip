import os
from os.path import isabs
from unittest.mock import MagicMock

import pytest

from paip.helpers import PipelineReseter


@pytest.fixture
def reseter():
    return PipelineReseter(pytest.helpers.file('Cohort1'))


def test_init(reseter):
    assert isabs(reseter.basedir)


def test_removable_files(reseter):
    files = reseter.removable_files

    assert pytest.helpers.file('Cohort1/Sample1/removable_file') in files
    assert pytest.helpers.file('Cohort1/removable_file') in files

    assert pytest.helpers.file('Cohort1/Sample1/Sample1.R1.fastq_report.html') in files
    assert pytest.helpers.file('Cohort1/Sample2/Sample2.R1.trimmed.fastq') in files

    assert pytest.helpers.file('Cohort1/Sample1/Sample1.R1.fastq') not in files
    assert pytest.helpers.file('Cohort1/Sample1/Sample1.R2.fastq') not in files

    assert pytest.helpers.file('Cohort1/sequencing_data.yml') not in files
    assert pytest.helpers.file('Cohort1/other_seq_data.yml') not in files

    assert pytest.helpers.file('Cohort1/non_removable_script.py') not in files
    assert pytest.helpers.file('Cohort1/non_removable_script.rb') not in files
    assert pytest.helpers.file('Cohort1/non_removable_script.sh') not in files


def test_reset_pipeline(reseter, monkeypatch):
    mock_remove = MagicMock()
    monkeypatch.setattr(os, 'remove', mock_remove)

    reseter.reset_pipeline(dry_run=True)
    assert mock_remove.call_count == 0

    reseter.reset_pipeline(dry_run=False)
    assert mock_remove.call_count == len(reseter.removable_files)

