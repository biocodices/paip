import json
import pytest

from paip.metrics_generation import PanelMetricsGenerator


@pytest.fixture(scope='function')
def pmg():
    return PanelMetricsGenerator(
        sample_vcf=pytest.helpers.file('Sample1_genos.vcf'),
        sample_name='Sample1',
        panel_vcf=pytest.helpers.file('panel_variants.vcf'),
        min_gq=30,
        min_dp=30,
    )


def test_init(pmg):
    assert len(pmg.panel) == 10
    assert pmg.panel_size == 10
    assert pmg.panel_ids == ['rs1;rs1_altname', 'rs2', 'rs3', 'rs4', 'rs5',
                             'rs6', 'rs7', 'rs99', 'rsX1', 'rsX2']
    assert len(pmg.genos) == 11  # 9 from the panel, 2 extra panel
    assert len(pmg.panel_genos) == 9
    assert 'GT' in pmg.genos
    assert 'DP' in pmg.genos
    assert 'GQ' in pmg.genos
    assert 'in_panel' in pmg.genos
    assert pmg.metrics == {}


def test_count_total_genos(pmg):
    pmg.count_total_genos()
    assert pmg.metrics['Total genos'] == 11


def test_count_seen_variants(pmg):
    pmg.count_seen_variants()
    assert pmg.metrics['Panel genos'] == 9
    assert pmg.metrics['Extra-panel genos'] == 2
    assert pmg.metrics['% Panel seen'] == 90.0  # 9/10

    # Now keep only the in-panel genotypes and test it doesn't break
    # trying to count the extra-panel genotypes (which are 0)
    pmg.genos = pmg.genos[pmg.genos['in_panel']].reset_index(drop=True)
    pmg.count_seen_variants()
    assert pmg.metrics['Extra-panel genos'] == 0


def test_count_missing_variants(pmg):
    pmg.count_missing_variants()
    assert pmg.metrics['Panel variants missing'] == 1
    assert pmg.metrics['% Panel missing'] == 10.0  # 1/10

    assert pmg.non_numerical_data['sample'] == 'Sample1'
    assert pmg.non_numerical_data['Panel missing IDs'] == ['rs99']
    panel_ids = ['rs1;rs1_altname', 'rs2', 'rs3', 'rs4', 'rs5', 'rs6', 'rs7',
                 'rsX1', 'rsX2']
    assert pmg.non_numerical_data['Panel seen IDs'] == panel_ids


def test_count_genotypes(pmg):
    pmg.count_genotypes()
    assert pmg.metrics['Panel 0/0'] == 3
    assert pmg.metrics['Panel 0/1'] == 2
    assert pmg.metrics['Panel 1/1'] == 3
    assert pmg.metrics['Panel ./.'] == 1


def test_compute_GQ_DP_stats(pmg):
    pmg.compute_GQ_DP_stats()
    assert pmg.metrics['DP mean'] == 123
    assert pmg.metrics['GQ mean'] == 89


def test_count_badqual_genotypes(pmg):
    pmg.count_badqual_genotypes()
    assert pmg.metrics['Panel non-reportable'] == 3
    assert pmg.metrics['Panel non-reportable %'] == 33.0  # 3/10
    assert pmg.metrics['Panel LowDP'] == 1
    assert pmg.metrics['Panel LowGQ'] == 1
    assert pmg.metrics['Panel non-PASS'] == 1


def test_belongs_to_panel(pmg):
    assert pmg.belongs_to_panel('rs1')
    assert pmg.belongs_to_panel('rs1_altname')
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

    def mock_count_badqual_genotypes():
        mock_count_badqual_genotypes.was_called = True

    def mock_compute_GQ_DP_stats():
        mock_compute_GQ_DP_stats.was_called = True

    mock_methods = {
        'count_total_genos': mock_count_total_genos,
        'count_seen_variants': mock_count_seen_variants,
        'count_missing_variants': mock_count_missing_variants,
        'count_genotypes': mock_count_genotypes,
        'count_badqual_genotypes': mock_count_badqual_genotypes,
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


def test_json_non_numerical_data(pmg):
    pmg.non_numerical_data = {'foo': ['bar', 'baz'], 'spam': 'eggs'}
    data = pmg.json_non_numerical_data()
    assert json.loads(data)['spam'] == 'eggs'

