from paip.pipelines.variant_calling import CallTargets


def test_run(sample_task_factory, mock_rename):
    task = sample_task_factory(CallTargets)
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk3 HaplotypeCaller target_sites'
    assert program_options['input_bam'] == \
        task.input()['alignment']['dupmarked_bam'].path
    assert '.vcf-luigi-tmp' in program_options['output_vcf']
    expected_out = '.hc_target_sites_realignment.bam-luigi-tmp'
    assert expected_out in program_options['output_bam']
    assert mock_rename.call_count == 4
