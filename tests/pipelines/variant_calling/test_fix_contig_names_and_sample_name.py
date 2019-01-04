from paip.pipelines.variant_calling import FixContigNamesAndSampleName


def test_fix_contig_names_and_sample_name(sample_task_factory, mock_rename):
    task = sample_task_factory(FixContigNamesAndSampleName,
                               sample_name="SampleWithExome")
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'cat' in command
    assert 'sed' in command

    assert task.input().path in command
    assert task.external_sample_name in command
    assert task.name in command
    assert 'contigs_fix.vcf-luigi-tmp' in kwargs['redirect_stdout_to_path']

    assert mock_rename.call_count == 1
