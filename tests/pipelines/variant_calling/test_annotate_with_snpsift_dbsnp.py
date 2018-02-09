from unittest.mock import mock_open, patch
import pytest

from paip.pipelines.variant_calling import AnnotateWithSnpsiftDbSNP, MergeVCFs, JointGenotyping


@pytest.fixture
def variant_sites_task(cohort_task_factory):
    return cohort_task_factory(AnnotateWithSnpsiftDbSNP)


@pytest.fixture
def target_sites_task(cohort_task_params):
    cohort_task_params['pipeline_type'] = 'target_sites'
    return AnnotateWithSnpsiftDbSNP(**cohort_task_params)


def test_requires_targets_pipeline(target_sites_task):
    expected_dependencies = MergeVCFs(**target_sites_task.param_kwargs)

    assert target_sites_task.requires() == expected_dependencies


def test_requires_variants_pipeline(variant_sites_task):
    expected_dependencies = JointGenotyping(**variant_sites_task.param_kwargs)

    assert variant_sites_task.requires() == expected_dependencies


def test_output(variant_sites_task, test_cohort_path):
    assert variant_sites_task.output().fn.endswith('.snpsift_dbsnp.vcf')


def test_run(variant_sites_task, test_cohort_path, monkeypatch):
    task = variant_sites_task
    open_ = mock_open()

    # FIXME: this whole 'path' to the module hardcoding is ugly, there must
    # be a better way:
    with patch('paip.pipelines.variant_calling.annotate_with_snpsift_dbsnp.open', open_):
        task.run()

    (program_name, program_options), kwargs = task.run_program.call_args
    assert program_name == 'snpsift dbSNP'
    assert program_options['input_vcf'] == task.input().fn
    assert kwargs['log_stdout'] is False
    open_().write.assert_called_once_with('stdout')

