from paip.pipelines.quality_control import SamtoolsStats


def test_run(sample_task_factory):
    task = sample_task_factory(SamtoolsStats)
    task.run()
    (program_name, program_options), kwargs = task.run_program.call_args
    assert program_name == 'samtools stats'
    assert program_options['input_bam'] == task.input().path
    assert task.output().path in kwargs['redirect_stdout_to_path']
