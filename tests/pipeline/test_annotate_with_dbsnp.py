import pytest

from paip.pipeline import AnnotateWithDbSNP, MergeVCFs, JointGenotyping


@pytest.fixture
def variant_sites_task(test_cohort_task_params):
    return AnnotateWithDbSNP(**test_cohort_task_params)


@pytest.fixture
def target_sites_task(test_cohort_task_params):
    test_cohort_task_params['pipeline_type'] = 'target_sites'
    return AnnotateWithDbSNP(**test_cohort_task_params)


def test_requires_targets_pipeline(target_sites_task):
    expected_dependencies = MergeVCFs(**target_sites_task.param_kwargs)

    assert target_sites_task.requires() == expected_dependencies


def test_requires_variants_pipeline(variant_sites_task):
    expected_dependencies = JointGenotyping(**variant_sites_task.param_kwargs)

    assert variant_sites_task.requires() == expected_dependencies


def test_output(variant_sites_task, test_cohort_path):
    expected = test_cohort_path('Cohort1__2_Samples.variant_sites.dbsnp.vcf')
    assert variant_sites_task.output().fn == expected


