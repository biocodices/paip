from paip.pipelines.quality_control import SamtoolsStats


def test_run(sample_task_factory):
    task = sample_task_factory(SamtoolsStats)
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'samtools stats' in command
    assert task.input()['dupmarked_bam'].path in command
    assert task.output().path in kwargs['redirect_stdout_to_path']
