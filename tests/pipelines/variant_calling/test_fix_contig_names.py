from paip.pipelines.variant_calling import FixContigNames


def test_fix_contig_names(sample_task_factory, mock_rename):
    task = sample_task_factory(FixContigNames)
    result = task.run()
    (program_name, program_options), kwargs = task.run_program.call_args

    assert program_name == 'fix contig names'
    assert program_options['input_vcf'] == task.input().path
    assert 'contigs_fix.vcf-luigi-tmp' in kwargs['redirect_stdout_to_path']
    assert mock_rename.call_count == 1
