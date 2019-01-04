from paip.pipelines.variant_calling import CallTargets


def test_run(sample_task_factory, mock_rename):
    task = sample_task_factory(CallTargets)
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'GenomeAnalysisTK.jar -T HaplotypeCaller' in command
    assert task.input()['alignment']['dupmarked_bam'].path in command
    assert '.vcf-luigi-tmp' in command
    assert '.hc_target_sites_realignment.bam-luigi-tmp' in command

    assert mock_rename.call_count == 4
