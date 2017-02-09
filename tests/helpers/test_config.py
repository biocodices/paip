import pytest

from paip.helpers import Config


def test_basic_usage(monkeypatch):
    monkeypatch.setattr(Config, 'BASE_DIR',
                        pytest.helpers.test_file('config_dir'))

    assert Config.read('foo') == {'foo': 'bar'}

    assert Config.parameters() == {'param-1': 'value-1'}
    assert Config.parameters('param-1') == 'value-1'

    assert Config.executables() == {'exec-1': 'value-1'}
    assert Config.resources() == {'resource-1': 'value-1'}
    assert Config.commands() == {'command-1': 'value-1'}

