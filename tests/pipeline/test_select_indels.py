import pytest

from paip.pipeline import SelectIndels, AnnotateWithDbSNP


@pytest.fixture
def task(test_cohort_task_params):
    return SelectIndels(**test_cohort_task_params)


def test_requires_targets_pipeline(task):
    expected_dependencies = AnnotateWithDbSNP(**task.param_kwargs)
    assert task.requires() == expected_dependencies


def test_output(task, test_cohort_path):
    fn = 'Cohort1__2_Samples.variant_sites.dbsnp.indels.vcf'
    expected_path = test_cohort_path(fn)
    assert task.output().fn == expected_path


