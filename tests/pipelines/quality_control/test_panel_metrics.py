from collections import defaultdict
from unittest.mock import mock_open, patch, MagicMock, PropertyMock

import pytest

import paip
from paip.pipelines.quality_control import PanelMetrics


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(PanelMetrics)


def test_run(task, monkeypatch):
    # This one is tricky to test. I need to mock the 'open' built-in,
    # but that breaks resources, so I need to mock that as well.
    # And then I need to mock the PMGenerator to check the init args.
    pmg_instance = MagicMock()
    PanelMetricsGenerator = MagicMock(return_value=pmg_instance)
    monkeypatch.setattr(paip.pipelines.quality_control.panel_metrics,
                        'PanelMetricsGenerator', PanelMetricsGenerator)
    mock_resources = patch('paip.helpers.config.Config.resources',
                           new_callable=PropertyMock)
    open_ = mock_open()
    #  mock_open_context = patch('paip.pipelines.quality_control.summarize_coverage.open',
                              #  open_)

    with patch('paip.pipelines.quality_control.panel_metrics.open', open_),\
         mock_resources as mock_resources:
        mock_resources.return_value = defaultdict(lambda: 'foo')
        task.run()

    assert PanelMetricsGenerator.call_count == 2
    assert PanelMetricsGenerator.call_args_list[0][1] == {
        'sample_name': task.sample,
        'sample_vcf': task.input()[0].fn,
        'panel_vcf': 'foo',
        'min_dp': task.min_dp,
        'min_gq': task.min_gq,
    }
    assert PanelMetricsGenerator.call_args_list[1][1] == {
        'sample_name': task.sample,
        'sample_vcf': task.input()[1].fn,
        'panel_vcf': 'foo',
        'min_dp': task.min_dp,
        'min_gq': task.min_gq,
    }

    assert open_().write.call_count == 4


def test_output(task):
    outs = task.output()
    assert outs[0].fn.endswith('unfiltered_variants_mqc.json')
    assert outs[1].fn.endswith('unfiltered_variants_data.json')
    assert outs[2].fn.endswith('reportable_variants_mqc.json')
    assert outs[3].fn.endswith('reportable_variants_data.json')

