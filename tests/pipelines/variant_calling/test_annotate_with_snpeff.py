from unittest.mock import mock_open, patch
import pytest

from paip.pipelines.variant_calling import AnnotateWithSnpeff


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(AnnotateWithSnpeff,
                               extra_params={'pipeline_type': 'variant_sites'})


def test_run(task):
    open_ = mock_open()

    # FIXME: this whole 'path' to the module hardcoding is ugly, there must
    # be a better way:
    with patch('paip.pipelines.variant_calling.annotate_with_snpeff.open', open_):
        task.run()

    (program_name, program_options), kwargs = task.run_program.call_args

    assert program_name == 'snpeff annotate'
    assert program_options['input_vcf'] == task.input().fn
    # Test the correct ending to snpeff summary is added:
    assert program_options['output_summary_csv'].endswith('snpEff.summary.csv')
    assert kwargs['log_stdout'] is False
    open_().write.assert_called_once_with('stdout')


def test_output(task, test_cohort_path):
    assert task.output().fn.endswith('.eff.vcf')

