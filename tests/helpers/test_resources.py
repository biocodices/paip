from paip.helpers import path_to_resource, available_resources


def test_path_to_resource(config_test_files):
    assert path_to_resource('resource-1b') == '/path/to/resource-1'


def test_available_resources(config_test_files):
    resources = available_resources()
    assert resources['resource-1'] == '/path/to/resource-1'

