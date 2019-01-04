from paip.pipelines.quality_control import VariantCallingMetrics


def test_run(sample_task_factory):
    task = sample_task_factory(VariantCallingMetrics)
    task.run()

    assert task.run_command.call_count == 1

    (command, ), kwargs = task.run_command.call_args

    assert 'picard-2.18.16.jar CollectVariantCallingMetrics' in command
    assert task.input().path in command
    assert command.endswith('Sample1.QC')
