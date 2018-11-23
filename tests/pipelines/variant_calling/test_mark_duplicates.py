from paip.pipelines.variant_calling import MarkDuplicates


def test_run(sample_task_factory, mock_rename):
    task = sample_task_factory(MarkDuplicates)
    task.run()
    (program_name, program_options), kwargs = task.run_program.call_args

    assert program_name == 'picard MarkDuplicates'
    assert program_options['input_bam'] == task.input().path
    assert mock_rename.call_count == 2 # Renames output BAM and metrics file
    assert task.output()['deduped_bam'].path + '-luigi' \
        in program_options['output_bam']
    assert task.output()['metrics_file'].path + '-luigi' \
        in program_options['output_metrics_file']
