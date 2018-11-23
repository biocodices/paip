from paip.pipelines.quality_control import DiagnoseTargets


def test_run(sample_task_factory, mock_rename):
    task = sample_task_factory(DiagnoseTargets)
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk3 DiagnoseTargets'
    assert program_options['input_bam'] == task.input().path
    assert program_options['min_dp'] == task.min_dp
    assert 'coverage_diagnosis.vcf-luigi-tmp' in program_options['output_vcf']
    assert mock_rename.call_count == 2
