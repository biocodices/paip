import pytest

from paip.pipelines.variant_calling import FilterIndels


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(FilterIndels)


def test_run(task):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk VariantFiltration indels'
    assert program_options['input_vcf'] == task.input().fn
    assert 'indels.filt.vcf-luigi-tmp' in program_options['output_vcf']
    assert task.rename_temp_idx.call_count == 1


def test_output(task, test_cohort_path):
    assert task.output().fn.endswith('indels.filt.vcf')

