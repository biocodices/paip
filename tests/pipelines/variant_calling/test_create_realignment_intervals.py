from paip.pipelines.variant_calling import CreateRealignmentIntervals


def test_run(sample_task_factory):
    task = sample_task_factory(CreateRealignmentIntervals)
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk3 RealignerTargetCreator'
    assert program_options['input_bam'] == task.input()['deduped_bam'].path
    assert 'realignment.intervals-luigi-tmp' in program_options['outfile']
