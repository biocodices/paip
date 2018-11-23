from paip.pipelines.variant_calling import SortCompressPutReadGroups


def test_run(sample_task_factory, mock_rename):
    task = sample_task_factory(SortCompressPutReadGroups)
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'picard AddOrReplaceReadGroups'
    assert program_options['input_sam'] == task.input().path
    assert program_options['library_id'] == 'Library-ID'
    assert program_options['flowcell_id'] == 'Flowcell-ID'
    assert program_options['lane_number'] == 'Lane-Number'
    assert program_options['platform'] == 'Platform'
    assert task.output().path + '-luigi-tmp' in program_options['output_bam']
    assert mock_rename.call_count == 2 # Renames BAM and BAI
