import json
import pytest

from paip.metrics_generation import PanelMetricsGenerator


@pytest.fixture(scope='function')
def pmg():
    return PanelMetricsGenerator(
        sample_vcf=pytest.helpers.file('Sample1_genos.vcf'),
        sample_name='Sample1',
        panel_vcf=pytest.helpers.file('panel_variants.vcf'),
    )


# Note:
# These tests use the vcfs Sample1_genos.vcf and panel_variants.vcf.
# The premise is that there are 8 genotypes in the Sample1 VCF,
# but only 5 of them are panel variants, the other 3 are extra panel.
# Additionally, 2 panel variants are not seen in the Sample1 VCF.


def test_init(pmg):
    assert len(pmg.panel) == 7
    assert len(pmg.genos) == 8
    assert pmg.panel_ids == ['rs1', 'rs2', 'rs3', 'rs4', 'rs5', 'rs9', 'rs10']
    assert pmg.panel_size == 7
    assert len(pmg.panel_genos) == 5
    assert 'GT' in pmg.genos
    assert 'DP' in pmg.genos
    assert 'GQ' in pmg.genos
    assert 'in_panel' in pmg.genos
    assert pmg.metrics == {}


def test_count_total_genos(pmg):
    pmg.count_total_genos()
    assert pmg.metrics['total_genos'] == 8


def test_count_seen_variants(pmg):
    pmg.count_seen_variants()
    assert pmg.metrics['panel_genotypes_seen'] == 5
    assert pmg.metrics['extra_panel_genotypes_seen'] == 3
    assert pmg.metrics['panel_genotypes_seen_%'] == 71.0  # 5/7

    # Now keep only the in-panel genotypes and test it doesn't break
    # trying to count the extra-panel genotypes (which are 0)
    pmg.genos = pmg.genos[pmg.genos['in_panel']].reset_index(drop=True)
    pmg.count_seen_variants()
    assert pmg.metrics['extra_panel_genotypes_seen'] == 0


def test_count_missing_variants(pmg):
    pmg.count_missing_variants()
    assert pmg.metrics['panel_genotypes_missing'] == 2
    assert pmg.metrics['panel_missing_%'] == 29.0  # 2/7


def test_count_genotypes(pmg):
    pmg.count_genotypes()
    assert pmg.metrics['panel_homRef_count'] == 2
    assert pmg.metrics['panel_het_count'] == 2
    assert pmg.metrics['panel_homAlt_count'] == 1
    assert pmg.metrics['panel_homRef_%'] == 40.0
    assert pmg.metrics['panel_het_%'] == 40.0
    assert pmg.metrics['panel_homAlt_%'] == 20.0


def test_compute_GQ_DP_stats(pmg):
    pmg.compute_GQ_DP_stats()
    assert pmg.metrics['DP_mean'] == 160
    assert pmg.metrics['DP_median'] == 200
    assert pmg.metrics['GQ_mean'] == 99
    assert pmg.metrics['GQ_median'] == 99


def test_belongs_to_panel(pmg):
    assert pmg.belongs_to_panel('rs1')
    assert not pmg.belongs_to_panel('rs8')


def test_percentage(pmg):
    assert pmg.percentage(15.5, 100) == 16.0


def test_compute_metrics(pmg, monkeypatch):
    def mock_count_total_genos():
        mock_count_total_genos.was_called = True

    def mock_count_seen_variants():
        mock_count_seen_variants.was_called = True

    def mock_count_missing_variants():
        mock_count_missing_variants.was_called = True

    def mock_count_genotypes():
        mock_count_genotypes.was_called = True

    def mock_compute_GQ_DP_stats():
        mock_compute_GQ_DP_stats.was_called = True

    mock_methods = {
        'count_total_genos': mock_count_total_genos,
        'count_seen_variants': mock_count_seen_variants,
        'count_missing_variants': mock_count_missing_variants,
        'count_genotypes': mock_count_genotypes,
        'compute_GQ_DP_stats': mock_compute_GQ_DP_stats,
    }

    for method_name, mock_method in mock_methods.items():
        monkeypatch.setattr(pmg, method_name, mock_method)

    pmg.compute_metrics()

    for method_name, mock_method in mock_methods.items():
        print(method_name)  # Included so pytest error is clearer
        assert mock_method.was_called


def test_json_metrics_for_multiqc(pmg):
    json_metrics = pmg.json_metrics_for_multiqc(module_name='module_foo')

    # Check that metrics have been generated
    assert pmg.metrics

    # Check the JSON result
    metrics = json.loads(json_metrics)
    assert metrics['data']['Sample1'] == pmg.metrics
    assert metrics['id'] == 'module_foo'

