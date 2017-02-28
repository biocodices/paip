import pytest

from paip.quality_control import VariantEval


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(VariantEval)


def test_run(task):
    task.run()
    result = task.run_program.args_received
    assert result['program_name'] == 'gatk VariantEval'
    assert result['program_options']['input_vcf'] == task.input().fn
    assert 'eval.grp-luigi-tmp' in result['program_options']['output_file']

