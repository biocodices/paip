import pytest

from paip.variant_calling import MakeGVCF


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(MakeGVCF)


def test_run(task):
    task.run()
    result = task.run_program.args_received

    assert result['program_name'] == 'gatk HaplotypeCaller'
    assert result['program_options']['input_bam'] == task.input().fn
    assert 'g.vcf-luigi-tmp' in result['program_options']['output_gvcf']
    expected_out = '.hc_realignment.bam-luigi-tmp'
    assert expected_out in result['program_options']['output_bam']
    assert task.rename_temp_bai.was_called
    assert task.rename_temp_idx.was_called

