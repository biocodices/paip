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
        > Config.commands()  # Same as Config.read('commands')
        > Config.resources()  # Same as Config.read('resources')

    You can also query keys inside each dictionary directly:

        > Config.parameters('foo')  # Searches the 'foo' key in parameters
        > Config.executables('foo')

    """
    BASE_DIR = expanduser('~/.paip')

    @classmethod
    def read(cls, yaml_filename):
        if not yaml_filename.endswith('.yml'):
            yaml_filename += '.yml'

        return yaml.load(open(join(cls.BASE_DIR, yaml_filename)))

    @classmethod
    def parameters(cls, key=None):
        dic = cls.read('parameters')
        return dic if key is None else dic[key]

    @classmethod
    def executables(cls, key=None):
        dic = cls.read('executables')
        return dic if key is None else dic[key]

    @classmethod
    def resources(cls, key=None):
        dic = cls.read('resources')
        return dic if key is None else dic[key]

    @classmethod
    def commands(cls, key=None):
        dic = cls.read('commands')
        return dic if key is None else dic[key]

