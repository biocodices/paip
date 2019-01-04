from paip.pipelines.quality_control import VariantEval


def test_run(sample_task_factory):
    task = sample_task_factory(VariantEval,
                               extra_params={'pipeline_type': 'variant_sites'})
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'GenomeAnalysisTK.jar -T VariantEval' in command
    assert task.input().path in command
    assert 'eval.grp-luigi-tmp' in command
