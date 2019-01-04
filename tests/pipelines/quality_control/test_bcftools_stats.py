from paip.pipelines.quality_control import BcftoolsStats


def test_run(sample_task_factory):
    task = sample_task_factory(BcftoolsStats,
                               extra_params={'pipeline_type': 'variant_sites'})
    task.run()
    (command, ), kwargs = task.run_command.call_args

    assert 'bcftools stats' in command
    assert task.input().path in command
    assert task.output().path in kwargs['redirect_stdout_to_path']
