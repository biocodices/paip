from unittest.mock import mock_open, patch, Mock

import pytest
import pandas as pd

import paip
from paip.pipelines.annotation.annotate_genes import AnnotateGenes


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


def test_read_gene_symbols(task):
    fp = pytest.helpers.file('snpEff.summary.genes.txt')
    gene_symbols = task.read_gene_symbols(fp)
    assert gene_symbols == ['GENE1' , 'GENE1-AS']


def test_gene_symbols_to_entrez_ids(task):
    result = task.gene_symbols_to_entrez_ids(['A1BG', 'NAT1'])
    assert result == [1, 9]


def test_run(task, monkeypatch):
    mock_read_gene_symbols = Mock(return_value=['GENE1'])
    monkeypatch.setattr(task, 'read_gene_symbols',
                        mock_read_gene_symbols)

    mock_gene_symbols_to_entrez_ids = Mock(return_value=[1])
    monkeypatch.setattr(task, 'gene_symbols_to_entrez_ids',
                        mock_gene_symbols_to_entrez_ids)

    mock_annotate_entrez_gene_ids = Mock(return_value=pd.DataFrame({}))
    monkeypatch.setattr(paip.pipelines.annotation.annotate_genes,
                        'annotate_entrez_gene_ids',
                        mock_annotate_entrez_gene_ids)

    mock_prettify_JSON_dump = Mock()
    monkeypatch.setattr(paip.pipelines.annotation.annotate_genes,
                        'prettify_JSON_dump', mock_prettify_JSON_dump)

    # Mock the open built-in function to test the output is written
    open_ = mock_open()
    with patch('paip.pipelines.annotation.annotate_genes.open', open_):
        task.requires()
        # ^ Simulate that requires() is called, which happens in the actual
        # pipeline. Without it, some args parsing is not done and the test
        # breaks.
        task.run()

    open_.assert_called_once_with(task.path('genes.json'), 'w')

    assert mock_read_gene_symbols.call_count == 1
    mock_gene_symbols_to_entrez_ids.assert_called_once_with(['GENE1'])
    mock_annotate_entrez_gene_ids.assert_called_once_with([1])
    assert mock_prettify_JSON_dump.call_count == 1
