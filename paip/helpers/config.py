import yaml
from os.path import join, expanduser, isfile


class Config:
    CONFIG_DIR = expanduser('~/.paip')

    def __init__(self, custom_config_dir=None):
        """
        If a *custom_config_dir* is provided, config files will be searched
        for there in addition to the CONFIG_DIR of this class. The definitions
        in the CONFIG_DIR files will be merged with the definitions in the custom
        config files, with priority for custom configs.

        Example:

            > config = Config(custom_config_dir="~/NGS-RUN-1")
            > config.read('parameters')
            # => Returns dict of ~/.paip/resources.yml, updated with the
            #    values at ~/NGS-RUN-1/resources.yml

            > config = Config()
            > # This wors fine as well, it just uses the ~/.paip/*.yml files.

        Some handy shortcuts:

            > config.executables
            > config.commands
            > config.resources

        You can also query keys inside each dictionary directly:

            > config.resources('human_genome')
            # => Searches the 'human_genome' key among the resources
            > config.executables('my-favorite-command')
        """
        self.custom_config_dir = custom_config_dir

    @property
    def commands(self):
        return self.read_and_merge('commands')

    @property
    def executables(self):
        return self.read_and_merge('executables')

    @property
    def resources(self):
        default_resources = self.read('resources')
        if self.custom_config_dir:
            custom_resources = self.read('resources',
                                         config_dir=self.custom_config_dir)
        else:
            custom_resources = {}

        default_resources_full_paths = self.make_full_paths_and_flatten(default_resources)
        custom_resources_full_paths = self.make_full_paths_and_flatten(custom_resources)

        return {**default_resources_full_paths, **custom_resources_full_paths}

    @classmethod
    def make_full_paths_and_flatten(cls, resources, key_prefix="",
                                    resources_dir=None):
        """
        *resources* should be a dictionary from a YAML like:

            resources_dir: /some/path/
            resource-1: file-1.txt
            resource-2: file-2.txt
            category:
                nested-resource: nested-resource.txt

        Generate a full path to each one of the *resources* filenames, keeping
        the keys intact, using the resources_dir under "resources_dir".
        Give special treatment to nested resources: put them under a level 0
        key like "category:nested-resource", joined with colons.

        Returns a flat dictionary with the full paths to all *resources*.
        """
        ret = {}

        if resources == {}:
            return ret

        resources_dir = resources_dir or resources['resources_dir']
        if not resources_dir:
            raise Exception('No "resources_dir" defined')

        for key, value in resources.items():
            if isinstance(value, str):
                ret[key] = join(resources_dir, value)
            elif isinstance(value, dict):
                nested_result = cls.make_full_paths_and_flatten(
                    value, key_prefix=key, resources_dir=resources_dir)
                ret.update(nested_result)
            else:
                msg = f'{key_prefix}:{key} has a non-dict and non-str value: {value}'
                raise ValueError(msg)

        if key_prefix:
            ret = {f'{key_prefix}:{key}': value for key, value in ret.items()}

        if 'resources_dir' in ret:
            del(ret['resources_dir'])

        return ret

    @classmethod
    def read(cls, yaml_filename, config_dir=None):
        if not yaml_filename.endswith('.yml'):
            yaml_filename += '.yml'
        filepath = join(config_dir or cls.CONFIG_DIR, yaml_filename)
        if isfile(filepath):
            return yaml.load(open(filepath))
        else:
            return {}

    def read_and_merge(self, yaml_filename):
        default_options = self.read(yaml_filename)
        custom_options = self.read(yaml_filename, config_dir=self.custom_config_dir)
        return {**default_options, **custom_options}
