from paip.pipelines.quality_control import FeatureCounts


def test_run(sample_task_factory):
    task = sample_task_factory(FeatureCounts)
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'featureCounts'
    assert program_options['input_bam'] == task.input()['dupmarked_bam'].path
    assert program_options['outfile'] == task.output().path
