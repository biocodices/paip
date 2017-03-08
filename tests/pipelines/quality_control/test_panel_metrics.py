import pytest

from paip.pipelines.quality_control import PanelMetrics


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(PanelMetrics)


def test_output(task):
    outs = task.output()
    assert outs[0].fn.endswith('variant_sites.unfiltered_variants_mqc.json')
    assert outs[1].fn.endswith('variant_sites.reportable_variants_mqc.json')

