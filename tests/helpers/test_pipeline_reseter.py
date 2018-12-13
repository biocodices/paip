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
    files_to_destroy = [
        'Cohort1/Sample1/removable_file',
        'Cohort1/removable_file',
        'Cohort1/Sample1/Sample1.R1.fastq_report.html',
        'Cohort1/Sample1/Sample1.R1_fastqc.zip',
        'Cohort1/Sample2/Sample2.R1.trimmed.fastq',
    ]
    files_to_keep = [
        'Cohort1/Sample1/Sample1.R1.fastq',
        'Cohort1/Sample1/Sample1.R2.fastq',
        'Cohort1/Sample1/Sample1.R1.fastq.gz',
        'Cohort1/Sample1/Sample1.R2.fastq.gz',
        'Cohort1/Sample1/Sample1.external_exome.vcf',
        'Cohort1/sequencing_data.yml',
        'Cohort1/other_seq_data.yml',
        'Cohort1/non_removable_script.py',
        'Cohort1/non_removable_script.rb',
        'Cohort1/non_removable_script.sh',
        'Cohort1/original_data/non_removable_file',
    ]

    files_considered_removable = reseter.removable_files
    for fn in files_to_destroy:
        assert pytest.helpers.file(fn) in files_considered_removable
    for fn in files_to_keep:
        assert pytest.helpers.file(fn) not in files_considered_removable


def test_reset_pipeline(reseter, monkeypatch):
    mock_remove = MagicMock()
    monkeypatch.setattr(os, 'remove', mock_remove)

    reseter.reset_pipeline(dry_run=True)
    assert mock_remove.call_count == 0

    reseter.reset_pipeline(dry_run=False)
    assert mock_remove.call_count == len(reseter.removable_files)

