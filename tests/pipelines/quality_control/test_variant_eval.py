from paip.pipelines.quality_control import VariantEval


def test_run(sample_task_factory):
    task = sample_task_factory(VariantEval,
                               extra_params={'pipeline_type': 'variant_sites'})
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'gatk3 VariantEval'
    assert program_options['input_vcf'] == task.input().path
    assert 'eval.grp-luigi-tmp' in program_options['output_file']
