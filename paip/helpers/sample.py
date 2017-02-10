from os.path import join


class Sample:
    """
    A simple class to generate filepaths associated to a given sample.
    All filepaths produced are under a subdir with the sample name.

    Usages:

        > Sample('SPL-1').path('{}.log')
          # => 'SPL-1/SPL-1.log'

        > Sample('SPL-2').paths(['{}.foo.txt', '{}.bar.txt'])
          # => ['SPL-2/SPL-2.foo.txt', 'SPL-2/SPL-2.bar.txt']

    """
    def __init__(self, sample_id):
        self.sample_id = sample_id

    def path(self, filename_template):
        """
        Given a filename that might contain format holes to fill in,
        return a path to a directory named after the sample and with the
        holes filled with the sample name.

        Example:

            > Sample('foo').path('{}.some_process.log')
              # => 'foo/foo.some_process.log'

        """
        return join(self.sample_id, filename_template.format(self.sample_id))

    def paths(self, filename_templates):
        return [self.path(filename) for filename in filename_templates]

