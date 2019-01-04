from paip.pipelines.variant_calling import AlignToReferenceAndAddReadGroup


def test_run(sample_task_factory):
    task = sample_task_factory(AlignToReferenceAndAddReadGroup)
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'bwa mem' in command

    # Read group options:
    assert 'Library-ID' in command
    assert 'Flowcell-ID' in command
    assert 'Lane1-Lane2' in command
    assert 'Platform' in command
    assert 'Platform_Unit' in command

    assert task.input()['forward_reads'].path in command
    assert task.input()['reverse_reads'].path in command
    assert task.output().path + '-luigi-tmp' in  kwargs['redirect_stdout_to_path']
