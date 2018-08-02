from collections import defaultdict
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from paip.pipelines.quality_control import PlotCoverage


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(PlotCoverage)


def test_run(task, monkeypatch):
    import paip

    ca_instance = MagicMock()
    CoverageAnalyser = MagicMock(return_value=ca_instance)

    monkeypatch.setattr(paip.pipelines.quality_control.plot_coverage,
                        'CoverageAnalyser', CoverageAnalyser)
    mock_resources = patch('paip.helpers.config.Config.resources',
                           new_callable=PropertyMock)

    with mock_resources as mock_resources:
        mock_resources.return_value = defaultdict(lambda: 'foo')
        task.run()

    assert CoverageAnalyser.call_count == 1
    assert CoverageAnalyser.call_args[1]['panel'] == 'foo'
    assert CoverageAnalyser.call_args[1]['reads_threshold'] == 30

    for fn in CoverageAnalyser.call_args[1]['coverage_files']:
        assert fn.endswith('coverage_diagnosis.vcf')

    assert ca_instance.report.call_count == 1

