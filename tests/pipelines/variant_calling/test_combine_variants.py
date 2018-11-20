import pytest

from paip.pipelines.variant_calling import CombineVariants


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(CombineVariants)


def test_run(task, test_cohort_path, mock_rename):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk3 CombineVariants snps_indels'
    assert program_options['input_snps'] == task.input()[0].path
    assert program_options['input_indels'] == task.input()[1].path
    assert 'filt.vcf-luigi-tmp' in program_options['output_vcf']
    assert mock_rename.call_count == 2


def test_output(task, test_cohort_path):
    assert task.output().path.endswith('filt.vcf')

