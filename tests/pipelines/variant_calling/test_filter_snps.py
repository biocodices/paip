import pytest

from paip.pipelines.variant_calling import FilterSNPs


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(FilterSNPs)


def test_run(task, test_cohort_path):
    task.run()

    assert task.run_program.call_count == 1
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk VariantFiltration snps'
    assert program_options['input_vcf'] == task.input().fn
    assert 'snps.filt.vcf-luigi-tmp' in program_options['output_vcf']

    assert task.rename_temp_idx.call_count == 1


def test_output(task, test_cohort_path):
    assert task.output().fn.endswith('snps.filt.vcf')
