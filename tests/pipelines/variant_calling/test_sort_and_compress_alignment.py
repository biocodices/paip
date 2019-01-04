from paip.pipelines.variant_calling import SortAndCompressAlignment


def test_run(sample_task_factory, mock_rename):
    task = sample_task_factory(SortAndCompressAlignment)
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'picard-2.18.16.jar SortSam' in command
    assert task.input()['alignment'].path in command
    assert task.output().path + '-luigi-tmp' in command

    assert mock_rename.call_count == 1
