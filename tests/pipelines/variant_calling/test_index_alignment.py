from paip.pipelines.variant_calling import IndexAlignment


def test_run(sample_task_factory, mock_rename):
    task = sample_task_factory(IndexAlignment)
    task.run()
    (program_name, program_options), kwargs = task.run_program.call_args

    assert program_name == 'picard BuildBamIndex'
    assert program_options['input_bam'] == task.input()['dupmarked_bam'].path
    assert task.output().path + '-luigi-tmp-' in program_options['output_bai']
    assert mock_rename.call_count == 1
