from paip.pipelines.variant_calling import IndexAlignment


def test_run(sample_task_factory, mock_rename):
    task = sample_task_factory(IndexAlignment)
    task.run()
    (program_name, program_options), kwargs = task.run_program.call_args

    assert program_name == 'picard BuildBamIndex'
    assert program_options['input_bam'] == task.input()['deduped_bam'].path
    assert mock_rename.call_count == 1
