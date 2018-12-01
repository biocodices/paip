from paip.pipelines.variant_calling import SortAndCompressAlignment


def test_run(sample_task_factory, mock_rename):
    task = sample_task_factory(SortAndCompressAlignment)
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'picard SortSam'
    assert program_options['input_sam'] == task.input()['alignment'].path
    assert task.output().path + '-luigi-tmp' in program_options['output_bam']
    assert mock_rename.call_count == 1
