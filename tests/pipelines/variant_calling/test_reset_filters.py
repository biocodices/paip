from paip.pipelines.variant_calling import ResetFilters


def test_run(sample_task_factory):
    task = sample_task_factory(ResetFilters)
    task.run()
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'bcftools reset_filters'
    assert program_options['input_vcf'] == task.input()[0].path
    assert program_options['output_vcf'] == task.output().path
