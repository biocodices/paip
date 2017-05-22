import pytest

from paip.helpers import Config


def test_basic_usage(config_test_files):
    assert Config.read('foo') == {'foo': 'bar'}
    assert Config.executables('program-1') == 'value-1'
    assert Config.resources('resource-1') == 'value-1'
    assert Config.commands('program-1') == ('value-1')

