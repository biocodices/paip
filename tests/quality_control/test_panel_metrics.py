import pytest

from paip.quality_control import PanelMetrics


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(PanelMetrics)


def test_output(task):
    out = task.output()
    assert out.fn.endswith('panel_metrics_mqc.yml')

