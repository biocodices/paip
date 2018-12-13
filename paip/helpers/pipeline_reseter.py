import os
from os.path import abspath, join
import re
import logging


logger = logging.getLogger(__name__)


class PipelineReseter:
    """
    Utility class to remove all files in a pipeline except for the FASTQs
    and configuration YAMLs.
    """
    PATTERNS_TO_KEEP = [
        r'.*original_data.*',
        r'\.(R1|R2)\.fastq$',
        r'\.(R1|R2)\.fastq\.gz$',
        r'\.external_exome\.vcf',
        r'\.rb$',
        r'\.py$',
        r'\.sh$',
        r'\.yml$',
        r'\.yaml$',
    ]

    def __init__(self, basedir):
        """Pass the base directory of the cohort."""
        self.basedir = abspath(basedir)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.basedir)

    @property
    def removable_files(self):
        """
        Recursively list the removable files in self.basedir. Keeps scripts
        ending in .py, .sh, or .rb, config files ending in .yml, and fastqs
        (but not trimmed fastqs).
        """
        removable_files = []

        for root, dirs, files in os.walk(self.basedir):
            for filename in files:
                filepath = join(root, filename)
                should_be_removed = True
                for pattern_to_keep in self.PATTERNS_TO_KEEP:
                    if re.search(pattern_to_keep, filepath):
                        should_be_removed = False
                        break

                if should_be_removed:
                    removable_files.append(filepath)

        return sorted(removable_files)

    def reset_pipeline(self, dry_run=True):
        """
        Remove all cohort files in self.basedir except for the YAML
        files and the samples R1.fastq(.gz) and R2.fastq(.gz) files.
        """
        if dry_run:
            logger.warning('Running in dry mode, no changes will be made.')

        del_count = 0
        for file_ in self.removable_files:
            if dry_run:
                logger.info('I would delete: {}'.format(file_))
            else:
                os.remove(file_)
                # ^ Please keep this as 'os.remove', and not as 'remove',
                # so that it can be mocked in the tests.
                del_count += 1

        if dry_run:
            logger.warning('Dry-run. I would have deleted {} files in {}'
                           .format(len(self.removable_files), self.basedir))
        else:
            logger.warning('Deleted {} files.'.format(del_count))
