from os.path import join, dirname

pytest_plugins = ['helpers_namespace']

import pytest

from paip.helpers import Config


@pytest.helpers.register
def test_file(filename):
    """Return the path to a file/dir under this repo's tests/files."""
    return join(dirname(__file__), 'files', filename)


@pytest.fixture(autouse=True)
def config_test_files(monkeypatch):
    # Read the Config files from tests/files/config_dir:
    monkeypatch.setattr(Config, 'BASE_DIR',
                        pytest.helpers.test_file('config_dir'))

    # BUT read the commands.yml from paip/example_config/commands.yml
    # so we don't have to mantain a copy of that file in the tests dir:
    def example_commands(key=None):
        example_dir = dirname(dirname(__file__))
        example_commands_yaml = 'paip/example_config/commands.yml'
        dic = Config.read(join(example_dir, example_commands_yaml))
        return dic if key is None else dic[key]

    monkeypatch.setattr(Config, 'commands', example_commands)

