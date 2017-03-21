from unittest.mock import MagicMock

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
    monkeypatch.setattr(paip.pipelines.quality_control.plot_coverage,
                        'path_to_resource', MagicMock(return_value='foo'))

    task.run()

    assert CoverageAnalyser.call_count == 1
    assert CoverageAnalyser.call_args[1]['panel_vcf'] == 'foo'
    assert CoverageAnalyser.call_args[1]['reads_threshold'] == 30

    for fn in CoverageAnalyser.call_args[1]['coverage_files']:
        assert fn.endswith('coverage_diagnosis.vcf')

    assert ca_instance.report.call_count == 1

