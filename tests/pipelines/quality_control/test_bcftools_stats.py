from paip.pipelines.quality_control import BcftoolsStats


def test_run(sample_task_factory):
    task = sample_task_factory(BcftoolsStats,
                               extra_params={'pipeline_type': 'variant_sites'})
    task.run()
    (program_name, program_options), kwargs = task.run_program.call_args
    assert program_name == 'bcftools stats'
    assert program_options['input_vcf'] == task.input().path
    assert task.output().path in kwargs['redirect_stdout_to_path']
