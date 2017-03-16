import pytest

from paip.pipelines.variant_calling import FilterGenotypes, CombineVariants


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(FilterGenotypes)


def test_requires(task):
    expected_dependencies = CombineVariants(**task.param_kwargs)
    assert task.requires() == expected_dependencies


def test_run(task, test_cohort_path, mock_rename):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk VariantFiltration genos'
    assert program_options['input_vcf'] == task.input().fn
    assert program_options['min_gq'] == task.min_gq
    assert program_options['min_dp'] == task.min_dp
    assert 'geno_filt.vcf-luigi-tmp' in program_options['output_vcf']
    assert mock_rename.call_count == 2


def test_output(task, test_cohort_path):
    assert task.output().fn.endswith('geno_filt.vcf')

