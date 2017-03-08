from unittest.mock import mock_open, patch
import pytest

from paip.pipelines.quality_control import BcftoolsStats


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(BcftoolsStats,
                               extra_params={'pipeline_type': 'variant_sites'})


def test_run(task):
    open_ = mock_open()

    # FIXME: this whole 'path' to the module hardcoding is ugly, there must
    # be a better way:
    with patch('paip.pipelines.quality_control.bcftools_stats.open', open_):
        task.run()

    (program_name, program_options), kwargs = task.run_program.call_args
    assert program_name == 'bcftools stats'
    assert program_options['input_vcf'] == task.input().fn
    assert kwargs['log_stdout'] is False
    open_().write.assert_called_once_with('stdout')

