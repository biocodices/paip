import pytest

from paip.pipelines.variant_calling import KeepReportableGenotypes, ExtractSample


@pytest.fixture
def task(cohort_task_factory):
    extra_params = {'sample': 'Sample1', 'min_dp': 30, 'min_gq': 30}
    return cohort_task_factory(KeepReportableGenotypes,
                               extra_params=extra_params)


def test_requires(task, cohort_task_params):
    expected_requires = ExtractSample(**cohort_task_params,
                                      sample=task.sample)
    assert task.requires() == expected_requires


def test_run(task, mock_rename):
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk SelectVariants reportable'
    program_input = program_options['input_vcf']
    assert program_input == task.input().fn
    assert 'reportable.vcf-luigi-tmp' in program_options['output_vcf']
    assert program_options['min_GQ'] == 30
    assert program_options['min_DP'] == 30
    assert program_options['sample'] == task.sample
    assert mock_rename.call_count == 2

