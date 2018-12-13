from paip.pipelines.variant_calling import FixContigNamesAndSampleName


def test_fix_contig_names_and_sample_name(sample_task_factory, mock_rename):
    task = sample_task_factory(FixContigNamesAndSampleName,
                               sample_name="SampleWithExome")
    result = task.run()
    (program_name, program_options), kwargs = task.run_program.call_args

    assert program_name == 'fix contig names and sample name'
    assert program_options['input_vcf'] == task.input().path
    assert program_options['external_sample_name'] == task.external_sample_name
    assert program_options['new_sample_name'] == task.name
    assert 'contigs_fix.vcf-luigi-tmp' in kwargs['redirect_stdout_to_path']
    assert mock_rename.call_count == 1
