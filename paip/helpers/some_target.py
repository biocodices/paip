from os.path import join
from glob import glob

import luigi


class SomeTarget(luigi.target.Target):
    """
    Subclass of luigi Target which asserts that the output exists if
    there are *one or more* files with the given suffix in the destination dir.
    Useful to check that some files of a kind have been created, without
    being specific about their filenames.

    Example:
        target = SomeTarget('/path/to/out', '.png')
        target.exists()
        # => Will return True if there are any PNG files under /path/to/out,
        #    for instance: /path/to/out/foo.png, and False otherwise.

    """
    def __init__(self, destination_dir, suffix):
        self.destination_dir = destination_dir
        self.suffix = suffix

    def exists(self):
        files = glob(join(self.destination_dir, '*' + self.suffix))
        return bool(files)

