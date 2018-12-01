from unittest.mock import mock_open, patch
from paip.pipelines.annotation_and_report import AnnotateWithSnpeff


def test_run(sample_task_factory):
    task = sample_task_factory(AnnotateWithSnpeff,
                               extra_params={'pipeline_type': 'variant_sites'})

    open_ = mock_open()

    # FIXME: this whole 'path' to the module hardcoding is ugly, but I need
    # the regular builtin open() to be operational for the rest of the code:
    with patch('paip.pipelines.annotation_and_report.annotate_with_snpeff.open', open_):
        task.run()

    (program_name, program_options), kwargs = task.run_program.call_args

    assert program_name == 'snpeff annotate'
    assert program_options['input_vcf'] == task.input().path
    # Test the correct ending to snpeff summary is added:
    assert program_options['output_summary_csv'].endswith('snpEff.summary.csv')
    assert kwargs['log_stdout'] is False
    open_().write.assert_called_once_with(b'stdout')
    assert task.output().path.endswith('.eff.vcf')
