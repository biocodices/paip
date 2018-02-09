import pytest

from paip.pipelines.annotation_and_report import AnnotateWithClinvar


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(AnnotateWithClinvar)


def test_requires(task):
    # NOTE: This is actually a test of CohortAnnotationTask working,
    # not of AnnotateWithClinvar specifically. It's easier to test it here
    # than in a separate test that would involve a mock class.
    # If you ever remove AnnotateWithClinvar, keep this test elsewhere:

    task.param_kwargs['cache'] = 'Cache-1'
    task.param_kwargs['http_proxy'] = 'Proxy-1'
    task.param_kwargs['extra_annotation_kwargs'] = '{"extra": "foo"}'

    required_task = task.requires()

    for key in ['http_proxy', 'cache', 'extra_annotation_kwargs']:
        assert key not in required_task.param_kwargs

    assert task.param_kwargs['cache'] == 'Cache-1'
    assert task.param_kwargs['http_proxy'] == 'Proxy-1'
    assert task.param_kwargs['extra_annotation_kwargs'] == '{"extra": "foo"}'

    assert not hasattr(required_task, 'annotation_kwargs')

    # These parameters were parsed/merged, notice that:
    assert task.annotation_kwargs['cache'] == 'Cache-1'
    assert task.annotation_kwargs['extra'] == 'foo'
    assert task.annotation_kwargs['proxies'] == {'http': 'Proxy-1'}


def test_output(task):
    assert task.output().fn.endswith('.clinvar_variants.json')
