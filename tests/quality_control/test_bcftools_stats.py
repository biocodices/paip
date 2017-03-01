import pytest

from paip.quality_control import BcftoolsStats


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(BcftoolsStats,
                               extra_params={'pipeline_type': 'variant_sites'})


def test_run(task):
    with pytest.raises(TypeError):
        # FIXME: This test is a hack, the failure is because we try to extract
        # stdout, stderr from run_command but its mock version returns None
        task.run()

    result = task.run_program.args_received
    assert result['program_name'] == 'bcftools stats'
    assert result['program_options']['input_vcf'] == task.input().fn

