from unittest.mock import mock_open, patch, MagicMock

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
    monkeypatch.setattr(paip.pipelines.quality_control.summarize_coverage,
                        'path_to_resource', MagicMock(return_value='foo'))

    open_ = mock_open()

    with patch('paip.pipelines.quality_control.summarize_coverage.open', open_):
        task.run()

    assert open_().write.call_count == 1

    assert ca_instance.json_coverage_summary_for_multiqc.call_count == 1
    assert ca_instance.coverage_summary.call_count == 1
    assert ca_instance.coverage_summary_per_gene.call_count == 1
    assert ca_instance.plot_coverage_distribution.call_count == 1
