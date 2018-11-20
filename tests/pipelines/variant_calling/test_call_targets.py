import pytest

from paip.pipelines.variant_calling import CallTargets


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(CallTargets)


def test_run(task, mock_rename):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk3 HaplotypeCaller target_sites'
    assert program_options['input_bam'] == task.input().path
    assert '.vcf-luigi-tmp' in program_options['output_vcf']
    expected_out = '.hc_target_sites_realignment.bam-luigi-tmp'
    assert expected_out in program_options['output_bam']
    assert mock_rename.call_count == 4

