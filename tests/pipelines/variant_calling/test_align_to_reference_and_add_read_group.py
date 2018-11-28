from paip.pipelines.variant_calling import AlignToReferenceAndAddReadGroup


def test_run(sample_task_factory):
    task = sample_task_factory(AlignToReferenceAndAddReadGroup)
    task.run()
    (program_name, program_options), kwargs = task.run_program.call_args

    assert program_name == 'bwa'

    # Read group options:
    assert program_options['library_id'] == 'Library-ID'
    assert program_options['flowcell_id'] == 'Flowcell-ID'
    assert program_options['lane_numbers_merged'] == 'Lane1-Lane2'
    assert program_options['platform'] == 'Platform'
    assert program_options['platform_unit'] == 'Platform_Unit'

    assert program_options['forward_reads'] == \
        task.input()['forward_reads'].path
    assert program_options['reverse_reads'] ==  \
        task.input()['reverse_reads'].path
    assert task.output().path + '-luigi-tmp' in  \
        kwargs['redirect_stdout_to_path']
