import os
import shutil
from tempfile import gettempdir
import pandas as pd
import pytest
import json
from glob import glob

from bs4 import BeautifulSoup

from paip.metrics_generation import CoverageAnalyser


panel_vcf = pytest.helpers.file('panel_variants.vcf')
files = ['Cohort1/Sample2/Sample2.coverage_diagnosis.vcf',
         'Cohort1/Sample3/Sample3.coverage_diagnosis.vcf']
coverage_files = [pytest.helpers.file(fn) for fn in files]


@pytest.fixture
def ca():
    return CoverageAnalyser(panel_vcf=panel_vcf,
                            coverage_files=coverage_files,
                            reads_threshold=20)


@pytest.fixture
def ca_single_sample():
    return CoverageAnalyser(panel_vcf=panel_vcf,
                            coverage_files=coverage_files[0:1],  # only one!
                            reads_threshold=20)


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


def test_make_coverage_matrix(ca):
    coverage_matrix = ca._make_coverage_matrix()

    assert coverage_matrix.shape == (2, 5)  # 5 intervals, 2 samples
    assert coverage_matrix.loc['Sample3', '[0005] X: 900–1,100'] == 2.49


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
    first_row = ca.intervals.iloc[0]
    assert first_row['interval_name'] == '1 : 900 – 1,100 | GENE1\nrs1;rs1_altname'
    assert first_row['interval_short_name'] == '[0001] 1: 900–1,100'


def test_init(ca):
    assert len(ca.panel) == 10  # 10 total panel variants
    assert len(ca.intervals) == 10  # 5 intervals diagnosed each sample
    assert ca.reads_threshold == 20

    for field in 'genes variants variants_count'.split():
        assert field in ca.intervals

    for field in 'interval_name interval_id'.split():
        assert field in ca.intervals


def test_plot_heatmap(ca):
    plot_file = ca.plot_heatmap(dest_dir=gettempdir(), max_value=30,
                                colormap='Oranges_r')

    assert os.path.isfile(plot_file)
    assert os.path.getsize(plot_file)

    os.remove(plot_file)
    assert not os.path.isfile(plot_file)


def test_plot_coverage_per_chromosome(ca):
    basename = os.path.join(gettempdir(), 'test_paip-cvg_plots')
    plot_files = ca.plot_coverage_per_chromosome(basename)

    # Test we save a plot for each chromosome with data
    for plot_file in plot_files:
        assert os.path.isfile(plot_file)
        assert os.path.getsize(plot_file)

        os.remove(plot_file)
        assert not os.path.isfile(plot_file)


def test_plot_file_chrom_index(ca):
    filename = '/path/to/plot_chrom_X.png'
    index = ca._plot_file_chrom_index(filename)
    assert index == 22


def test_make_html_report(ca):
    report_filepath = os.path.join(gettempdir(),
                                   'paip_test-coverage_report.html')
    chromosome_plots = ['/path/to/plot_chrom_1.png',
                        '/path/to/plot_chrom_X.png']
    heatmap_plot = '/path/to/heatmap.png'

    ca.make_html_report(
        report_title='Report Title',
        heatmap_plot=heatmap_plot,
        chromosome_plots=chromosome_plots,
        destination_path=report_filepath,
    )

    assert os.path.isfile(report_filepath)
    assert os.path.getsize(report_filepath)

    with open(report_filepath) as f:
        html_written = f.read()

    assert 'Report Title' in html_written

    soup = BeautifulSoup(html_written, 'html.parser')

    for plot_filename in chromosome_plots + [heatmap_plot]:
        found_images = soup.select('img[src="{}"]'.format(plot_filename))
        assert len(found_images) == 1

    os.remove(report_filepath)
    assert not os.path.isfile(report_filepath)


def test_report(ca):
    given_path = os.path.join(gettempdir(), 'paip_test-cov_report')
    result_path = ca.report('Report Title', given_path)

    # Check .html is added to the filename if not present
    assert result_path.endswith('.html')

    # Check the plots dir is created
    expected_plots_dir = os.path.join(os.path.dirname(given_path),
                                      'coverage_plots')
    assert os.path.isdir(expected_plots_dir)

    # Check the plots are saved there
    cvg_plots = glob(os.path.join(expected_plots_dir, '*coverage*.png'))
    assert len(cvg_plots) == 3

    heatmap_plots = glob(os.path.join(expected_plots_dir, '*heatmap*.png'))
    assert len(heatmap_plots) == 1

    # Remove files after testing
    os.remove(result_path)
    assert not os.path.isfile(result_path)

    shutil.rmtree(expected_plots_dir)
    assert not os.path.isdir(expected_plots_dir)


def test_summarize_coverage(ca_single_sample):
    data = ca_single_sample.summarize_coverage()
    assert data['NO_READS intervals'] == 1
    assert data['% bases with LOW DP'] == 40.9
    assert data['mean_DP'] == 1003.28
    assert data['std_DP'] == 1062.02


def test_json_coverage_summary_for_multiqc(ca_single_sample):
    json_data = ca_single_sample.json_coverage_summary_for_multiqc(
        sample_id='SampleFoo', module_name='module_foo',
    )
    data = json.loads(json_data)
    assert 'id' in data
    assert 'data' in data
    assert 'SampleFoo' in data['data']
