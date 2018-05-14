import os
from os import getpid
from tempfile import gettempdir
import pandas as pd
import pytest
import json
from glob import glob
import shutil
from unittest.mock import MagicMock

from bs4 import BeautifulSoup

from paip.metrics_generation import CoverageAnalyser


panel_vcf = pytest.helpers.file('panel_variants.vcf')
panel_bed = pytest.helpers.file('panel_regions.bed')
panel_csv = pytest.helpers.file('panel_regions.csv')
files = ['Cohort1/Sample2/Sample2.coverage_diagnosis.vcf',
         'Cohort1/Sample3/Sample3.coverage_diagnosis.vcf']
coverage_files = [pytest.helpers.file(fn) for fn in files]


@pytest.fixture
def ca():
    return CoverageAnalyser(panel=panel_vcf,
                            coverage_files=coverage_files,
                            reads_threshold=20)

@pytest.fixture
def ca_csv_panel():
    return CoverageAnalyser(panel=panel_csv,
                            coverage_files=coverage_files,
                            reads_threshold=20)


@pytest.fixture
def ca_no_panel():
    return CoverageAnalyser(coverage_files=coverage_files,
                            reads_threshold=20)


@pytest.fixture
def ca_single_sample():
    return CoverageAnalyser(panel=panel_vcf,
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
    ca._read_panel_from_vcf = MagicMock()
    ca._add_panel_vcf_data_to_intervals = MagicMock()
    ca._read_panel(panel_vcf)
    ca._read_panel_from_vcf.assert_called_once
    ca._add_panel_vcf_data_to_intervals.assert_called_once()

    ca._read_panel_from_bed = MagicMock()
    ca._read_panel(panel_bed)
    ca._read_panel_from_bed.assert_called_once

    ca._read_panel_from_csv = MagicMock()
    ca._add_panel_csv_data_to_intervals = MagicMock()
    ca._read_panel(panel_csv)
    ca._read_panel_from_csv.assert_called_once
    ca._add_panel_csv_data_to_intervals.assert_called_once()


def test_read_panel_from_csv(ca):
    panel = ca._read_panel_from_csv(panel_csv)
    assert len(panel) == 5
    assert list(panel['variants'])[:2] == ['rs1a_rs1b', 'rs2a_rs2b']
    assert list(panel['genes'])[:2] == ['GENE1', 'GENE2']
    assert list(panel['sources'])[:2] == ['Pheno1', 'Pheno2a_Pheno2b']


def test_read_panel_from_vcf(ca):
    panel = ca._read_panel_from_vcf(panel_vcf)
    assert all(isinstance(chrom, str) for chrom in panel['chrom'])
    assert all(isinstance(genes, tuple) for genes in panel['genes'])
    assert list(panel['varclass']) == ['SNV'] * 5 + ['DIV'] + [None] * 4

    for field in 'qual filter info ref alt'.split():
        assert field not in panel


def test_read_panel_from_bed(ca):
    panel = ca._read_panel_from_bed(panel_bed)
    assert all(isinstance(chrom, str) for chrom in panel['chrom'])
    features = ['Feature-1', 'Feature-2', 'Feature-3', 'Feature-X']
    assert features == list(panel['genes'])


def test_read_coverage_files(ca):
    intervals = ca._read_coverage_files(coverage_files)
    assert all(isinstance(val, int) for val in intervals['LL'])
    assert all(isinstance(val, int) for val in intervals['ZL'])
    assert all(isinstance(val, float) for val in intervals['IDP'])
    assert 'end_pos' in intervals
    assert all(isinstance(val, int) for val in intervals['end_pos'])
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


def test_coverage_summary(ca_csv_panel):
    result = ca_csv_panel.coverage_summary()
    assert '[Intergenic]' in result['Gene'].values
    first_entry = result.iloc[0]
    assert first_entry['Gene'] == 'GENE1'
    assert first_entry['Interval Length'] == 201
    assert first_entry['Interval Variants'] == 'rs1a, rs1b'
    assert first_entry['Interval Status'] == 'PASS'
    assert first_entry['Interval Mean Coverage'] == 406.5
    assert first_entry['Associated Conditions'] == 'Pheno1'

    fp = os.path.join(gettempdir(), f'test__coverage_summary_{getpid()}.csv')
    result = ca_csv_panel.coverage_summary(target_csv_path=fp)

    assert os.path.isfile(fp)
    assert os.path.getsize(fp)

    os.remove(fp)
    assert not os.path.isfile(fp)


def test_coverage_summary_per_gene(ca_csv_panel):
    result = ca_csv_panel.coverage_summary_per_gene()
    first_entry = result.iloc[0]
    assert first_entry['Gene'] == 'GENE1'
    assert first_entry['Variant Count'] == 2
    assert first_entry['Coverage Average'] == 407.5
    assert first_entry['Associated Conditions'] == 'Pheno1'
    assert first_entry['Min Coverage'] == 406.5
    assert first_entry['Max Coverage'] == 408.5
    assert first_entry['Filters'] == None

    fp = os.path.join(gettempdir(),
                      f'test__coverage_summary_per_gene_{getpid()}.csv')
    result = ca_csv_panel.coverage_summary(target_csv_path=fp)

    assert os.path.isfile(fp)
    assert os.path.getsize(fp)

    os.remove(fp)
    assert not os.path.isfile(fp)


def test_add_panel_vcf_data_to_intervals(ca):
    ca.panel = ca._read_panel_from_vcf(panel_vcf)
    ca._add_panel_vcf_data_to_intervals()
    assert list(ca.intervals['genes']) == [
        ('GENE1',), ('GENE1',), ('GENE1',), ('GENE2',), ('GENE3', 'GENE4')
    ] * 2
    assert list(ca.intervals['variants']) == [
        ('rs1;rs1_altname',), ('rs2',), ('rs3',), ('rs5',), ('rsX1',),
    ] * 2
    assert list(ca.intervals['variants_count']) == [1] * 5 * 2


@pytest.mark.skip(reason="Write this test!")
def test_add_panel_data_to_intervals_from_bed():
    CoverageAnalyser(coverage_files, panel=panel_bed)


def test_add_panel_csv_data_to_intervals(ca_no_panel):
    ca = ca_no_panel
    ca.panel = ca._read_panel_from_csv(panel_csv)
    ca._add_panel_csv_data_to_intervals()
    assert list(ca.intervals['genes'])[:2] == ['GENE1', 'GENE2']
    assert list(ca.intervals['sources'])[:2] == ['Pheno1', 'Pheno2a_Pheno2b']
    assert list(ca.intervals['variants'])[:2] == ['rs1a_rs1b', 'rs2a_rs2b']
    assert list(ca.intervals['variants_count'])[:2] == [2, 2]


def test_make_coverage_matrix(ca_no_panel, ca_csv_panel):
    coverage_matrix = ca_no_panel._make_coverage_matrix()
    assert coverage_matrix.shape == (2, 5)  # 5 intervals, 2 samples
    assert coverage_matrix.loc['Sample3', '[0005] X: 900–1,100'] == 2.49

    coverage_matrix = ca_csv_panel._make_coverage_matrix()
    assert coverage_matrix.shape == (2, 5)  # 5 intervals, 2 samples
    assert coverage_matrix.loc['Sample3', '1: 900–1,100 (x2) | GENE1 | Pheno1'] == 408.50


def test_define_sample_colors_and_markers(ca):
    ca._define_sample_colors_and_markers()

    assert ca.sample_colors == {
        'Sample2': (0.86, 0.3712, 0.33999999999999997),
        'Sample3': (0.86, 0.6832, 0.33999999999999997),
    }
    assert ca.sample_markers == {
        'Sample2': 'x',
        'Sample3': 'o',
    }


def test_generate_interval_names(ca, ca_csv_panel):
    ca._generate_interval_names()
    first_row = ca.intervals.iloc[0]
    assert first_row['interval_name'] == '1: 900–1,100'
    assert first_row['interval_name_with_index'] == '[0001] 1: 900–1,100'

    ca = ca_csv_panel
    ca._generate_interval_names()
    first_row = ca.intervals.iloc[0]
    assert first_row['interval_name'] == '1: 900–1,100'
    assert first_row['interval_name_with_index'] == '[0001] 1: 900–1,100'


def test_add_interval_names_with_info(ca, ca_csv_panel):
    # The tested method is already called on initialization
    # This is not pretty, I should rewrite it.
    first_row = ca.intervals.iloc[0]
    assert first_row['interval_name_with_info'] == \
        '1: 900–1,100 | GENE1\nrs1;rs1_altname'

    ca = ca_csv_panel
    first_row = ca.intervals.iloc[0]
    assert first_row['interval_name_with_info'] == \
        '1: 900–1,100 (x2) | GENE1 | Pheno1'

def test_init(ca):
    assert len(ca.panel) == 10  # 10 total panel variants
    assert len(ca.intervals) == 10  # 5 intervals diagnosed each sample
    assert ca.reads_threshold == 20

    for field in 'genes variants variants_count'.split():
        assert field in ca.intervals

    for field in 'interval_name interval_id'.split():
        assert field in ca.intervals


def test_init_without_panel_vcf():
    ca = CoverageAnalyser(coverage_files=coverage_files)
    assert not ca.has_panel


def test_samples_property(ca_no_panel):
    assert list(ca_no_panel.samples) == ['Sample2', 'Sample3']


def test_plots_without_saving(ca):
    heatmap = ca.plot_heatmap(max_value=30)
    boxplot = ca.plot_boxplot()
    violinplot = ca.plot_violinplot()
    chromosomes = ca.plot_coverage_per_chromosome(plt_show=False)
    coverage_dist = ca.plot_coverage_distribution()

    from matplotlib.axes import Axes

    assert isinstance(heatmap, Axes)
    assert isinstance(boxplot, Axes)
    assert isinstance(violinplot, Axes)
    assert isinstance(chromosomes[0], Axes)
    assert isinstance(coverage_dist, Axes)


def test_plot_heatmap(ca):
    plot_file = ca.plot_heatmap(dest_dir=gettempdir(), max_value=30,
                                colormap='Oranges_r')

    assert os.path.isfile(plot_file)
    assert os.path.getsize(plot_file)

    os.remove(plot_file)
    assert not os.path.isfile(plot_file)


def test_plot_boxplot(ca):
    plot_file = ca.plot_boxplot(dest_dir=gettempdir())

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


def test_plot_coverage_distribution(ca):
    plot_file = ca.plot_coverage_distribution(dest_dir=gettempdir())

    assert os.path.isfile(plot_file)
    assert os.path.getsize(plot_file)

    os.remove(plot_file)
    assert not os.path.isfile(plot_file)


def test_make_html_report(ca):
    report_filepath = os.path.join(gettempdir(),
                                   'paip_test-coverage_report.html')
    chrom_plots = ['/path/to/plot_chrom_1.png',
                   '/path/to/plot_chrom_X.png']
    heatmap = '/path/to/heatmap.png'
    boxplot = '/path/to/boxplot.png'

    ca.make_html_report(
        template_data={
            'report_title': 'Report Title',
            'boxplot_path': boxplot,
            'heatmap_path': heatmap,
            'chrom_plot_paths': chrom_plots,
        },
        destination_path=report_filepath,
    )

    assert os.path.isfile(report_filepath)
    assert os.path.getsize(report_filepath)

    with open(report_filepath) as f:
        html_written = f.read()

    assert 'Report Title' in html_written

    soup = BeautifulSoup(html_written, 'html.parser')

    for plot_filename in [boxplot, heatmap] + chrom_plots:
        found_images = soup.select('img[src="{}"]'.format(plot_filename))
        assert len(found_images) == 1

    os.remove(report_filepath)
    assert not os.path.isfile(report_filepath)


def test_report(ca):
    basename = os.path.join(gettempdir(), 'paip_test-cov_report')
    report_path = ca.report('Report Title', basename)

    # Check .html is added to the filename if not present
    assert report_path.endswith('.html')

    # Check the plots dir is created
    plots_dir = os.path.join(os.path.dirname(basename), 'coverage_plots')
    assert os.path.isdir(plots_dir)

    # NOT DRAWING THESE PLOTS FOR NOW:

    # Check the plots are saved there
    #  cvg_plots = glob(os.path.join(plots_dir, '*coverage_chrom*.png'))
    #  assert len(cvg_plots) == 2

    heatmaps = glob(os.path.join(plots_dir, '*heatmap*.png'))
    assert len(heatmaps) == 2

    boxplots = glob(os.path.join(plots_dir, '*boxplot*.png'))
    assert len(boxplots) == 2

    violinplots = glob(os.path.join(plots_dir, '*violinplot*.png'))
    assert len(violinplots) == 1

    # Remove files after testing
    os.remove(report_path)
    assert not os.path.isfile(report_path)

    shutil.rmtree(plots_dir)
    assert not os.path.isdir(plots_dir)


def test_summarize_coverage_for_multiqc(ca_single_sample):
    data = ca_single_sample.summarize_coverage_for_multiqc()
    assert data['NO_READS intervals'] == 1
    assert data['% bases with LOW DP'] == 40.9
    assert data['mean_DP'] == 1003.08
    assert data['std_DP'] == 1062.13


def test_json_coverage_summary_for_multiqc(ca_single_sample):
    json_data = ca_single_sample.json_coverage_summary_for_multiqc(
        sample_id='SampleFoo', module_name='module_foo',
    )
    data = json.loads(json_data)
    assert 'id' in data
    assert 'data' in data
    assert 'SampleFoo' in data['data']
