import yaml
from os.path import join, expanduser


class Config:
    """
    This class is not meant to be initialized. Check the usage:

    Example:

        > Config.read('parameters')  # Returns dict of ~/.paip/parameters.yml

    Some handy shortcuts:

        > Config.parameters()  # Same as Config.read('parameters')
        > Config.executables()  # Same as Config.read('executables')
        > Config.resources()  # Same as Config.read('resources')
    """
    @classmethod
    def read(cls, yaml_filename):
        if not yaml_filename.endswith('.yml'):
            yaml_filename += '.yml'

        base_dir = expanduser('~/.paip')
        return yaml.load(open(join(base_dir, yaml_filename)))

    @classmethod
    def parameters(cls):
        return cls.read('parameters')

    @classmethod
    def executables(cls):
        return cls.read('executables')

    @classmethod
    def resources(cls):
        return cls.read('resources')

