from unittest.mock import mock_open, patch, MagicMock
import pytest

import paip.pipelines.annotation_and_report.annotate_variants
from paip.pipelines.annotation_and_report.annotate_variants import AnnotateVariants


@pytest.fixture
def task(cohort_task_factory):
    extra_params = {
        'cache': 'cache_name',
        'http_proxy': 'some_proxy',
        'extra_annotation_kwargs': '{"extra_param": "extra_param_value"}'
    }
    return cohort_task_factory(AnnotateVariants, extra_params=extra_params)


def test_run(task, monkeypatch):
    # Mock the AnnotationPipeline class so it returns a mocked instance:
    pipeline_instance = MagicMock()
    AnnotationPipeline = MagicMock(return_value=pipeline_instance)
    prettify_JSON_dump_mock = MagicMock()
    monkeypatch.setattr(paip.pipelines.annotation_and_report.annotate_variants,
                        'AnnotationPipeline', AnnotationPipeline)
    monkeypatch.setattr(paip.pipelines.annotation_and_report.annotate_variants,
                        'prettify_JSON_dump', prettify_JSON_dump_mock)

    # Mock the open built-in function to test the output is written
    open_ = mock_open()
    with patch('paip.pipelines.annotation_and_report.annotate_variants.open', open_):
        task.requires()
        # ^ Simulate that requires() is called, which happens in the actual
        # pipeline. Without it, some args parsing is not done and the test
        # breaks.
        task.run()

    assert AnnotationPipeline.call_count == 1
    assert AnnotationPipeline.call_args[1] == {
        'cache': 'cache_name',
        'proxies': {'http': 'some_proxy'},
        'extra_param': 'extra_param_value',
    }

    pipe_run = pipeline_instance.run_from_vcf
    assert pipe_run.call_count == 1
    assert pipe_run.call_args[0][0] == task.input().path

    assert pipeline_instance.rs_variants.to_json.call_count == 1
    assert pipeline_instance.rs_variants.to_json.call_args[1] == \
        {'orient': 'split'}
    assert pipeline_instance.other_variants.to_json.call_count == 1
    assert pipeline_instance.other_variants.to_json.call_args[1] == \
        {'orient': 'split'}

    assert prettify_JSON_dump_mock.call_count == 2
    assert prettify_JSON_dump_mock.call_count == 2

    # I don't write genes.json in this task anymore:
    #  assert pipeline_instance.gene_annotations.to_json.call_count == 1
    #  assert pipeline_instance.gene_annotations.to_json.call_args[1] == \
        #  {'orient': 'split'}

    assert open_().write.call_count == 2
