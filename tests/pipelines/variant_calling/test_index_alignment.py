from paip.pipelines.variant_calling import IndexAlignment


def test_run(sample_task_factory, mock_rename):
    task = sample_task_factory(IndexAlignment)
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'picard-2.18.16.jar BuildBamIndex' in command
    assert task.input()['dupmarked_bam'].path in command
    assert task.output().path + '-luigi-tmp-' in command

    assert mock_rename.call_count == 1
