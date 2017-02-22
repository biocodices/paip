import pytest

from paip.pipeline import JointGenotyping, MakeGVCF


@pytest.fixture
def task(basedir):
    return JointGenotyping(basedir=basedir,
                           samples='Sample1,Sample2',
                           pipeline_type='variant_sites')


def test_output(task, test_cohort_path):
    expected_path = test_cohort_path('Cohort1__2_Samples.variant_sites.vcf')
    assert task.output().fn == expected_path


def test_requires(task):
    expected_dependencies = [
        MakeGVCF(sample='Sample1', pipeline_type='variant_sites'),
        MakeGVCF(sample='Sample2', pipeline_type='variant_sites')
    ]

    assert task.requires() == expected_dependencies

