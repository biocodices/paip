from paip.pipelines.variant_calling import ResetFilters


def test_run(sample_task_factory):
    task = sample_task_factory(ResetFilters)
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'bcftools annotate --remove FILTER,QUAL' in command
    assert task.input()[0].path in command
    assert task.output().path in command
