import pytest

from paip.pipelines.quality_control import DiagnoseTargets


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(DiagnoseTargets)


def test_run(task):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk DiagnoseTargets'
    assert program_options['input_bam'] == task.input().fn
    assert 'coverage_diagnosis.vcf-luigi-tmp' in program_options['output_vcf']
    assert task.rename_temp_idx.call_count == 1

