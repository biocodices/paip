from paip.pipelines.ion_torrent import TorrentVariantCaller


def test_run(sample_task_factory, mock_rename):
    task = sample_task_factory(TorrentVariantCaller,
                               sample_name='Sample1',
                               cohort_name='IonCohort')
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'python2.7' in command
    assert 'variant_caller_plugin.py' in command
    assert 'Sample1.fix.bam' in command

    assert mock_rename.call_count == 9

    rename_call_args = mock_rename.call_args_list[0]
    assert 'TSVC_variants.vcf.gz' in rename_call_args[0][0]
    assert 'Sample1.vcf.gz' in rename_call_args[0][1]

    rename_call_args = mock_rename.call_args_list[1]
    assert 'TSVC_variants.vcf.gz.tbi' in rename_call_args[0][0]
    assert 'Sample1.vcf.gz.tbi' in rename_call_args[0][1]

    rename_call_args = mock_rename.call_args_list[2]
    assert 'TSVC_variants.genome.vcf.gz' in rename_call_args[0][0]
    assert 'Sample1.genome.vcf.gz' in rename_call_args[0][1]

    rename_call_args = mock_rename.call_args_list[3]
    assert 'TSVC_variants.genome.vcf.gz.tbi' in rename_call_args[0][0]
    assert 'Sample1.genome.vcf.gz.tbi' in rename_call_args[0][1]

    rename_call_args = mock_rename.call_args_list[4]
    assert 'black_listed.vcf' in rename_call_args[0][0]
    assert 'Sample1.black_listed.vcf' in rename_call_args[0][1]

    rename_call_args = mock_rename.call_args_list[5]
    assert 'depth.txt' in rename_call_args[0][0]
    assert 'Sample1.depth.txt' in rename_call_args[0][1]

    rename_call_args = mock_rename.call_args_list[6]
    assert 'indel_assembly.vcf' in rename_call_args[0][0]
    assert 'Sample1.indel_assembly.vcf' in rename_call_args[0][1]

    rename_call_args = mock_rename.call_args_list[7]
    assert 'small_variants_filtered.vcf' in rename_call_args[0][0]
    assert 'Sample1.small_variants_filtered.vcf' in rename_call_args[0][1]

    rename_call_args = mock_rename.call_args_list[8]
    assert 'small_variants.vcf' in rename_call_args[0][0]
    assert 'Sample1.small_variants.vcf' in rename_call_args[0][1]
