import pytest

from paip.pipelines.variant_calling import SelectIndels


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(SelectIndels)


def test_run(task, test_cohort_path):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk SelectVariants indels'
    assert program_options['input_vcf'] == task.input().fn
    assert 'indels.vcf-luigi-tmp' in program_options['output_vcf']
    assert task.rename_temp_idx.call_count == 1


def test_output(task):
    assert task.output().fn.endswith('indels.vcf')

