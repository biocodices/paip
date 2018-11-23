from paip.pipelines.variant_calling import CreateRecalibrationTable


def test_run(sample_task_factory):
    task = sample_task_factory(CreateRecalibrationTable)
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk3 BaseRecalibrator'
    assert program_options['input_bam'] == task.input().path
    assert 'recalibration_table-luigi-tmp' in program_options['outfile']
