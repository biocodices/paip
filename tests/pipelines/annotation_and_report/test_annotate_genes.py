from unittest.mock import mock_open, patch, Mock

import pytest
import pandas as pd

import anotamela.pipeline
import paip.pipelines.annotation_and_report.annotate_genes
from paip.pipelines.annotation_and_report.annotate_genes import (
    AnnotateGenes,
    extract_entrez_gene_ids_from_vep_tsv,
)


@pytest.fixture
def vep_tsv_path():
    return pytest.helpers.file('vep_annotations.tsv')


@pytest.fixture
def task(cohort_task_factory):
    extra_params = {
        'cache': 'cache_name',
        'http_proxy': 'some_proxy',
        'extra_annotation_kwargs': '{"extra_param": "extra_param_value"}'
    }
    return cohort_task_factory(AnnotateGenes, extra_params=extra_params)


def test_extract_entrez_gene_ids_from_vep_tsv(vep_tsv_path):
    result = extract_entrez_gene_ids_from_vep_tsv(vep_tsv_path)
    assert result == ['123', '234']


def test_run(task, monkeypatch):
    mock_gene_annotations = pd.DataFrame({})
    mock_annotate_entrez_gene_ids = Mock(return_value=mock_gene_annotations)
    monkeypatch.setattr(paip.pipelines.annotation_and_report.annotate_genes,
                        'annotate_entrez_gene_ids',
                        mock_annotate_entrez_gene_ids)
    monkeypatch.setattr(paip.pipelines.annotation_and_report.annotate_genes,
                        'extract_entrez_gene_ids_from_vep_tsv',
                        Mock())

    # Mock the open built-in function to test the output is written
    open_ = mock_open()
    with patch('paip.pipelines.annotation_and_report.annotate_genes.open', open_):
        task.requires()
        # ^ Simulate that requires() is called, which happens in the actual
        # pipeline. Without it, some args parsing is not done and the test
        # breaks.
        task.run()

    open_.assert_called_once_with(task.path('genes.json'), 'w')
