from paip.helpers import Sample

import pytest


def test_path():
    assert Sample('S1').path('{}.txt') == 'S1/S1.txt'


def test_paths():
    assert Sample('S1').paths(['{}.log', '{}.txt']) == ['S1/S1.log',
                                                        'S1/S1.txt']


def test_load_sequencing_data_from_yaml():
    sample = Sample('Sample1')
    seq_data_yaml = pytest.helpers.test_file('sequencing_data.yml')
    sample.load_sequencing_data_from_yaml(seq_data_yaml)

    assert sample.sequencing_id == 'Seq1'
    assert sample.library_id == 'Lib1'
    assert sample.id_in_sequencing == 'Spl1'

