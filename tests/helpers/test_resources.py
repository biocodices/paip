from paip.helpers import path_to_resource, available_resources


def test_path_to_resource():
    assert path_to_resource('indels_1000G') == '/path/to/indels_1000G.vcf'


def test_available_resources():
    resources = available_resources()
    assert resources['dbsnp_GRCh37'] == '/path/to/dbsnp_GRCh37.vcf'
