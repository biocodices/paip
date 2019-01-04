from paip.pipelines.variant_calling import MakeGVCF


def test_run(sample_task_factory, mock_rename):
    task = sample_task_factory(MakeGVCF)
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'gatk HaplotypeCaller' in command
    assert task.input()['alignment']['dupmarked_bam'].path in command
    assert 'g.vcf-luigi-tmp' in command
    assert '.HC_haplotypes.bam-luigi-tmp' in command

    assert mock_rename.call_count == 4
