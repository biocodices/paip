from paip.pipelines.variant_calling import RecalibrateAlignmentScores


def test_run(sample_task_factory, mock_rename):
    task = sample_task_factory(RecalibrateAlignmentScores)
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk3 PrintReads'
    assert program_options['input_bam'] == task.input()[0].path
    assert program_options['recalibration_table'] == task.input()[1].path
    assert 'recalibrated.bam-luigi-tmp' in program_options['output_bam']
    assert mock_rename.call_count == 2
