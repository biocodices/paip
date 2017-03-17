import pytest

from paip.metrics_generation import CoverageAnalyser


@pytest.fixture
def ca():
    files = ['Cohort1/Sample2/Sample2.coverage_diagnosis.vcf',
             'Cohort1/Sample3/Sample3.coverage_diagnosis.vcf']

    return CoverageAnalyser(
        panel_vcf=pytest.helpers.file('panel_variants.vcf'),
        coverage_files=[pytest.helpers.file(fn) for fn in files],
    )


def test_init(ca):
    assert len(ca.panel) == 10  # 10 total panel variants
    assert len(ca.intervals) == 10  # 5 intervals diagnosed each sample


def test_read_panel():
    # SEGUIR ACÁ TESTEAR cada método!
    #  CoverageAnalyser._read_panel
    pass

