import pytest

from paip.pipelines.annotation_and_report import AnnotateWithGeneEntrez


@pytest.fixture
def task(cohort_task_factory):
    extra_params = {
        'cache': 'cache_name',
        'http_proxy': 'some_proxy',
        'extra_annotation_kwargs': '{"extra_param": "extra_param_value"}'
    }
    return cohort_task_factory(AnnotateWithGeneEntrez, extra_params=extra_params)


def test_output(task):
    assert task.output().path.endswith('.gene_entrez_annotations.json')


def test_extract_gene_entrez_ids_from_dbsnp_annotations(task):
    fn = task.input().path # Cohort1/Cohort1.dbsnp_annotations.json
    result = AnnotateWithGeneEntrez._extract_gene_entrez_ids_from_dbsnp_annotations(fn)
    assert result == [1, 2, 3]


def test_run(task):
    # This is too complex to test. It could be done, copying the way I'm
    # testing in test_annotate_variants.py, but it seems so cumbersome
    # that it looks like a wasted effort.
    # There must be a better way.
    pass

