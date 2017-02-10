from paip.helpers import Sample


def test_path():
    assert Sample('S1').path('{}.txt') == 'S1/S1.txt'


def test_paths():
    assert Sample('S1').paths(['{}.log', '{}.txt']) == ['S1/S1.log',
                                                        'S1/S1.txt']

