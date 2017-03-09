import pytest

from paip.pipelines.variant_calling import MakeGVCF


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(MakeGVCF)


def test_run(task):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk HaplotypeCaller'
    assert program_options['input_bam'] == task.input().fn
    assert 'g.vcf-luigi-tmp' in program_options['output_gvcf']
    assert '.hc_realignment.bam-luigi-tmp' in program_options['output_bam']
    assert task.rename_temp_bai.call_count == 1
    assert task.rename_temp_idx.call_count == 1

