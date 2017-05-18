from unittest.mock import mock_open, patch, MagicMock
import pytest

import paip.pipelines.variant_calling.annotate_variants
from paip.pipelines.variant_calling.annotate_variants import AnnotateVariants


@pytest.fixture
def task(cohort_task_factory):
    extra_params = {
        'cache': 'cache_name',
        'http_proxy': 'some_proxy',
        'annotation_kwargs': '{"extra_param": "extra_param_value"}'
    }
    return cohort_task_factory(AnnotateVariants, extra_params=extra_params)


def test_run(task, monkeypatch):
    # Mock the AnnotationPipeline class and the returned instance:
    pipeline_instance = MagicMock()
    AnnotationPipeline = MagicMock(return_value=pipeline_instance)
    monkeypatch.setattr(paip.pipelines.variant_calling.annotate_variants,
                        'AnnotationPipeline', AnnotationPipeline)

    # Mock the open built-in function to test the output is written
    open_ = mock_open()
    with patch('paip.pipelines.variant_calling.annotate_variants.open', open_):
        task.run()

    assert AnnotationPipeline.call_count == 1
    assert AnnotationPipeline.call_args[1] == {
        'cache': 'cache_name',
        'proxies': {'http': 'some_proxy'},
        'extra_param': 'extra_param_value',
    }

    pipe_run = pipeline_instance.run_from_vcf
    assert pipe_run.call_count == 1
    assert pipe_run.call_args[0][0] == task.input().fn

    assert pipeline_instance.rs_variants.to_json.call_count == 1
    assert pipeline_instance.rs_variants.to_json.call_args[1] == \
        {'orient': 'split'}
    assert pipeline_instance.gene_annotations.to_json.call_count == 1
    assert pipeline_instance.gene_annotations.to_json.call_args[1] == \
        {'orient': 'split'}

    open_().write.call_count == 2

