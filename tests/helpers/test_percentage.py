from paip.helpers import percentage


def test_percentage():
    assert percentage(15.5, 100) == 16.0

