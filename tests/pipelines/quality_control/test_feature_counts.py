from paip.pipelines.quality_control import FeatureCounts


def test_run(sample_task_factory):
    task = sample_task_factory(FeatureCounts)
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'featureCounts' in command
    assert task.input()['dupmarked_bam'].path in command
    assert task.output().path in command
