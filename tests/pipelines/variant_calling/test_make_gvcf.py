from paip.pipelines.variant_calling import MakeGVCF


def test_run(sample_task_factory, mock_rename):
    task = sample_task_factory(MakeGVCF)
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk4 HaplotypeCaller'
    assert program_options['input_bam'] == \
        task.input()['alignment']['dupmarked_bam'].path
    assert 'g.vcf-luigi-tmp' in program_options['output_gvcf']
    assert '.HC_haplotypes.bam-luigi-tmp' in program_options['output_bam']
    assert mock_rename.call_count == 4
