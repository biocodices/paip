from paip.pipelines.variant_calling import MarkDuplicates


def test_run(sample_task_factory, mock_rename):
    task = sample_task_factory(MarkDuplicates)
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'picard-2.18.16.jar MarkDuplicates' in command
    assert task.input().path in command
    assert task.output()['dupmarked_bam'].path + '-luigi' in command
    assert task.output()['metrics_file'].path in command

    assert mock_rename.call_count == 1
