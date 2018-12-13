import pytest

from paip.pipelines.variant_calling import KeepReportableGenotypes


def test_run(cohort_task_factory, mock_rename):
    task = cohort_task_factory(KeepReportableGenotypes,
                               extra_params={'sample': 'Sample1',
                                             'min_dp': 30,
                                             'min_gq': 30})

    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk3 SelectVariants reportable'
    program_input = program_options['input_vcf']
    assert program_input == task.input().path
    assert 'reportable.vcf-luigi-tmp' in program_options['output_vcf']
    assert program_options['min_GQ'] == 30
    # assert program_options['min_DP'] == 30
    assert program_options['sample'] == task.sample
    assert mock_rename.call_count == 2
