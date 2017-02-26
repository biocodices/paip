import pytest

from paip.variant_calling import AnnotateWithDbSNP, MergeVCFs, JointGenotyping


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
    assert variant_sites_task.output().fn.endswith('dbsnp.vcf')


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

    program_input = result['program_options']['input_vcf']
    assert program_input == variant_sites_task.input().fn

