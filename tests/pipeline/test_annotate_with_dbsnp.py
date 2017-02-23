import os
import re
from io import StringIO

import pytest

import paip
from paip.pipeline import AnnotateWithDbSNP, MergeVCFs, JointGenotyping


@pytest.fixture
def variant_sites_task(cohort_task_factory):
    return cohort_task_factory(AnnotateWithDbSNP)


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


def test_run(variant_sites_task, test_cohort_path, monkeypatch):
    with pytest.raises(TypeError):
        # This will fail because mock_run_program
        # doesn't return (stdout, stderr). I'd rather
        # have it fail there than later in the open function,
        # which I can't patch, see:
        # http://doc.pytest.org/en/latest/monkeypatch.html
        variant_sites_task.run()
        # It's ok anyway, I can test the rest of the run():

    result = variant_sites_task.run_program.args_received

    assert result['program_name'] == 'snpsift dbSNP'
    assert result['log_stdout'] is False

    seen_input = result['program_options']['input_vcf']
    expected_input_fn = 'Cohort1__2_Samples.variant_sites.vcf'
    expected_input = test_cohort_path(expected_input_fn)
    assert seen_input == expected_input

    assert not variant_sites_task.rename_temp_idx.was_called
    assert not variant_sites_task.rename_temp_bai.was_called

