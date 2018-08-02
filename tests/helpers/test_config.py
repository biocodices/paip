import pytest

from paip.helpers import Config


CUSTOM_CONFIG_DIR = pytest.helpers.file('Cohort1')

@pytest.fixture
def config(config_test_files):
    return Config(custom_config_dir=CUSTOM_CONFIG_DIR)

def test_read(config_test_files):
    assert Config.read('foo') == {'foo': 'bar', 'baz': 'bam'}
    assert Config.read('foo', config_dir=CUSTOM_CONFIG_DIR) == \
        {'foo': 'custom-bar'}

    assert Config.read('non-existent-yaml') == {}


def test_read_and_merge(config):
    assert config.read_and_merge('foo') == {
        'foo': 'custom-bar', # This value came from the custom config dir
        'baz': 'bam' # This value came from the default config dir
    }


def test_shortcuts(config):
    assert config.commands == {
        'program-1': 'custom-program-1',
        'program-2': ('{executable} --foo {foo_option} --bar {bar_option} '
                      '--resource {resource-1}')
    }
    assert config.executables == {
        'program-1': 'custom-executable-1',
        'program-2': 'executable-2',
    }
    assert config.resources == {
        'resource-1': '/other/path/to/resource-1-modified.txt',
        'resource-2': '/path/to/resource-2.txt',
        'category:nested-resource': '/path/to/nested-resource.txt',
        'category:category-2:very-nested-resource': \
                '/other/path/to/very-nested-resource.txt',
    }

    config = Config(custom_config_dir=None)
    assert config.resources == {
        'resource-1': '/path/to/resource-1.txt',
        'resource-2': '/path/to/resource-2.txt',
        'category:nested-resource': '/path/to/nested-resource.txt',
    }
