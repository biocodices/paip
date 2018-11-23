from paip.pipelines.quality_control import AlignmentMetrics


def test_run(sample_task_factory):
    task = sample_task_factory(AlignmentMetrics)
    task.run()

    assert task.run_program.call_count == 1
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'picard CollectAlignmentSummaryMetrics'
    assert program_options['input_bam'] == task.input().path
    assert 'alignment_metrics.txt-luigi-tmp' in program_options['output_txt']
