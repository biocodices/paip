from collections import defaultdict
from unittest.mock import mock_open, patch, MagicMock, PropertyMock

import pytest

import paip
from paip.pipelines.quality_control import SummarizeCoverage


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(SummarizeCoverage)


def test_run(task, monkeypatch):
    ca_instance = MagicMock()
    CoverageAnalyser = MagicMock(return_value=ca_instance)

    monkeypatch.setattr(paip.pipelines.quality_control.summarize_coverage,
                        'CoverageAnalyser', CoverageAnalyser)
    mock_resources = patch('paip.helpers.config.Config.resources',
                           new_callable=PropertyMock)
    open_ = mock_open()
    mock_open_context = patch('paip.pipelines.quality_control.summarize_coverage.open',
                              open_)

    with mock_open_context, mock_resources as mock_resources:
        mock_resources.return_value = defaultdict(lambda: 'foo')
        task.run()

    assert open_().write.call_count == 1

    assert ca_instance.json_coverage_summary_for_multiqc.call_count == 1
    assert ca_instance.coverage_summary.call_count == 1
    assert ca_instance.coverage_summary_per_gene.call_count == 1
    assert ca_instance.plot_coverage_distribution.call_count == 1
