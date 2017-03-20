from unittest.mock import MagicMock
import pandas as pd
import pytest

from paip.metrics_generation import CoverageAnalyser


panel_vcf = pytest.helpers.file('panel_variants.vcf')
files = ['Cohort1/Sample2/Sample2.coverage_diagnosis.vcf',
         'Cohort1/Sample3/Sample3.coverage_diagnosis.vcf']
coverage_files = [pytest.helpers.file(fn) for fn in files]


@pytest.fixture
def ca():
    return CoverageAnalyser(panel_vcf=panel_vcf,
                            coverage_files=coverage_files)


def test_extract_genes(ca):
    genes = ca._extract_genes({'GENEINFO': 'Gene_1:1'})
    assert genes == ['Gene_1']

    genes = ca._extract_genes({'GENEINFO': 'Gene_1:1|Gene_2:2'})
    assert genes == ['Gene_1', 'Gene_2']

    genes = ca._extract_genes({})
    assert genes == []


def test_read_panel(ca):
    panel = ca._read_panel(panel_vcf)
    assert all(isinstance(chrom, str) for chrom in panel['chrom'])
    assert all(isinstance(genes, tuple) for genes in panel['genes'])
    assert list(panel['varclass']) == ['SNV'] * 5 + ['DIV'] + [None] * 4

    for field in 'qual filter info ref alt'.split():
        assert field not in panel


def test_read_coverage_files(ca):
    intervals = ca._read_coverage_files(coverage_files)
    from numpy import int64, float64
    assert all(isinstance(val, int64) for val in intervals['LL'])
    assert all(isinstance(val, int64) for val in intervals['ZL'])
    assert all(isinstance(val, float64) for val in intervals['IDP'])
    assert 'end_pos' in intervals
    assert all(isinstance(val, int64) for val in intervals['end_pos'])
    assert 'length' in intervals
    assert list(intervals['length']) == [201] * 10
    assert list(intervals['sample_id']) == ['Sample2'] * 5 + ['Sample3'] * 5


def test_find_variants(ca):
    interval = pd.Series({'chrom': 'X', 'pos': 1900, 'end_pos': 2100})
    variants = ca._find_variants(interval, ca.panel)
    assert list(variants['id']) == ['rsX2']

    interval['chrom'] = '19'
    variants = ca._find_variants(interval, ca.panel)
    assert variants.empty

    #  with pytest.raises
    interval['chrom'] = 1  # Chrom as integer!
    with pytest.raises(AssertionError):
        ca._find_variants(interval, ca.panel)

    # Test cache is built
    assert 'X:1900:2100' in CoverageAnalyser._find_variants_cache
    assert '19:1900:2100' in CoverageAnalyser._find_variants_cache


def test_find_genes(ca):
    interval = pd.Series({'chrom': 'X', 'pos': 900, 'end_pos': 1100})
    genes = ca._find_genes(interval, ca.panel)
    assert genes == ['GENE3', 'GENE4']

    interval['chrom'] = '1'
    genes = ca._find_genes(interval, ca.panel)
    assert genes == ['GENE1']

    interval['chrom'] = '19'
    genes = ca._find_genes(interval, ca.panel)
    assert genes == []


def test_find_variant_ids(ca):
    interval = pd.Series({'chrom': 'X', 'pos': 900, 'end_pos': 1100})
    variants = ca._find_variant_ids(interval, ca.panel)
    assert variants == ['rsX1']

    interval['chrom'] = '1'
    variants = ca._find_variant_ids(interval, ca.panel)
    assert variants == ['rs1;rs1_altname']

    interval['chrom'] = '19'
    variants = ca._find_variant_ids(interval, ca.panel)
    assert variants == []


def test_add_panel_data_to_intervals(ca):
    ca.panel = ca._read_panel(panel_vcf)
    ca._add_panel_data_to_intervals()
    assert list(ca.intervals['genes']) == [
        ('GENE1',), ('GENE1',), ('GENE1',), ('GENE2',), ('GENE3', 'GENE4')
    ] * 2
    assert list(ca.intervals['variants']) == [
        ('rs1;rs1_altname',), ('rs2',), ('rs3',), ('rs5',), ('rsX1',),
    ] * 2
    assert list(ca.intervals['variants_count']) == [1] * 5 * 2


def test_define_sample_colors_and_markers(ca):
    ca._define_sample_colors_and_markers()

    assert ca.sample_colors == {
        'Sample2': (0.12156862745098039, 0.4666666666666667, 0.7058823529411765),
        'Sample3': (1.0, 0.4980392156862745, 0.054901960784313725),
    }
    assert ca.sample_markers == {
        'Sample2': 'x',
        'Sample3': 'o',
    }


def test_generate_interval_names(ca):
    ca._generate_interval_names()
    assert list(ca.intervals['interval_name']) == [
        '1:900-1100 | GENE1 (1 variants)',
        '1:1900-2100 | GENE1 (1 variants)',
        '1:2900-3100 | GENE1 (1 variants)',
        '1:4900-5100 | GENE2 (1 variants)',
        'X:900-1100 | GENE3, GENE4 (1 variants)'
    ] * 2


def test_init(ca):
    assert len(ca.panel) == 10  # 10 total panel variants
    assert len(ca.intervals) == 10  # 5 intervals diagnosed each sample

    for field in 'genes variants variants_count'.split():
        assert field in ca.intervals

    for field in 'interval_name interval_id'.split():
        assert field in ca.intervals


# NOTE: This is tricky to test, I would need to patch pandas.DataFrame.plot

def test_plot(ca, monkeypatch):
    import paip
    import pandas

    pyplot = MagicMock()
    pandas_plot = MagicMock()

    monkeypatch.setattr(paip.metrics_generation.coverage_analyser, 'plt', pyplot)
    monkeypatch.setattr(pandas.DataFrame, 'plot', pandas_plot)

    ca.plot('/path/to/plot')

    # Test we save a plot for each chromosome with data
    assert pyplot.savefig.call_count == 2
    assert pyplot.savefig.call_args_list[0][0][0] == '/path/to/plot_chrom_1.png'
    assert pyplot.savefig.call_args_list[1][0][0] == '/path/to/plot_chrom_X.png'

    assert pandas_plot.scatter.call_count == 4  # 2 chroms * 2 samples

