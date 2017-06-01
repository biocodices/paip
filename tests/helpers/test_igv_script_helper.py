from os import getpid, remove
from os.path import join, dirname, isfile
from tempfile import gettempdir
import pytest

from paip.helpers import IGVScriptHelper


VCF = pytest.helpers.file('Cohort1/Sample1/Sample1_genos.vcf')
TEMPLATE_PATH = join(dirname(dirname(dirname(__file__))),
                     'paip', 'example_config', 'igv_batch_template')


@pytest.fixture
def helper():
    return IGVScriptHelper(
        vcf=VCF,
        template_path=TEMPLATE_PATH,
        template_data={'foo': 'bar'}
    )


def test_init(helper):
    assert helper.template_data['foo'] == 'bar'


def test_read_template(helper):
    template = helper._read_template()
    assert 'IGV Batch script template' in template


def test_data_for_template(helper):
    data = helper._data_for_template()
    assert data['foo'] == 'bar'
    assert data['reference_genome_hg19'].endswith('human_g1k_v37.fasta')


def test_read_variants_file(helper):
    variants = helper._read_variants_file()
    assert variants[0] == {
        'chrom': '1',
        'id': 'rs1_altname',
        'pos': 1000,
        'range_around': 'chr1:920-1080',
        'dest_filename': '1_1000_rs1_altname.png',
    }


def test_write_script():
    template_data = {
        'sample_igv_snapshots_dir': '/path/to/snapshots_dir',
        'sample_alignment': '/path/to/sample.bam',
        'sample_alignment_trackname': 'sample.bam',
        'sample_all_variants': '/path/to/sample.vcf',
        'sample_reportable_variants': '/path/to/sample_reportable.vcf',
        'cohort_variants': '/path/to/cohort.vcf',
    }

    helper = IGVScriptHelper(
        vcf=VCF,
        template_path=TEMPLATE_PATH,
        template_data=template_data
    )
    out_path = join(gettempdir(), 'test_script_' + str(getpid()))
    helper.write_script(out_path)

    with open(out_path) as f:
        written_script = f.read()

    # This testing is not exhaustive, but will do:
    assert 'goto chr1:920-1080' in written_script
    assert 'snapshot 1_1000_rs1_altname.png' in written_script

    # Cleanup
    remove(out_path)
    assert not isfile(out_path)

