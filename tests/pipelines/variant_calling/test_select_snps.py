import pytest

from paip.pipelines.variant_calling import SelectSNPs


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(SelectSNPs)


def test_run(task, mock_rename):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk SelectVariants snps'
    assert program_options['input_vcf'] == task.input().fn
    assert 'snps.vcf-luigi-tmp' in program_options['output_vcf']
    assert mock_rename.call_count == 2


def test_output(task):
    assert task.output().fn.endswith('snps.vcf')

