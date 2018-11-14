import pytest

from paip.pipelines.variant_calling import FilterIndels


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(FilterIndels)


def test_run(task, mock_rename):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk VariantFiltration indels'
    assert program_options['input_vcf'] == task.input().path
    assert 'indels.filt.vcf-luigi-tmp' in program_options['output_vcf']
    assert mock_rename.call_count == 2


def test_output(task):
    assert task.output().path.endswith('indels.filt.vcf')

