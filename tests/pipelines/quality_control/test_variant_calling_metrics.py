from paip.pipelines.quality_control import VariantCallingMetrics


def test_run(sample_task_factory):
    task = sample_task_factory(VariantCallingMetrics)
    task.run()

    assert task.run_program.call_count == 1
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'picard CollectVariantCallingMetrics'
    assert program_options['input_vcf'] == task.input().path
    assert program_options['output_txt'].endswith('QC')
