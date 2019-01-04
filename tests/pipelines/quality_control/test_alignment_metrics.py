from paip.pipelines.quality_control import AlignmentMetrics


def test_run(sample_task_factory):
    task = sample_task_factory(AlignmentMetrics)
    task.run()

    assert task.run_command.call_count == 1

    (command, ), kwargs = task.run_command.call_args

    assert 'picard-2.18.16.jar CollectAlignmentSummaryMetrics' in command
    assert 'Sample1.dupmarked_alignment.bam' in command
    assert 'alignment_metrics.txt-luigi-tmp' in command
