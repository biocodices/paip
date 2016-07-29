#!/usr/bin/env python
"""

cd to the parent directory of your data dir and run this script without any
arguments. It will copy all the .fastq files to a new results directory (which
will be created if it doesn't exist). Then, it will create a subfolder for each
different sample. It assumes that the .fastq filenames follow this format:

    <sample-id>.<R1 or R2, according to forward or reverse>.fastq

Usage:

    prepare_directories.py
    prepare_directories -h | --help

"""


import re
import os
from os.path import join, basename, isfile
from glob import glob
from shutil import copy2
from docopt import docopt


def main():
    base_dir = os.getcwd()
    results_dir = join(base_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)

    for fastq_file in sorted(glob(join(base_dir, 'data/*.fastq'))):
        sample_id = re.search(r'(.+).R[12].fastq',
                              basename(fastq_file)).group(1)
        sample_dir = join(base_dir, 'results/%s' % sample_id)
        os.makedirs(sample_dir, exist_ok=True)

        destination_file = join(sample_dir, basename(fastq_file))
        if isfile(destination_file):
            print('Exists: ./results/%s/%s' % (sample_id, basename(fastq_file)))
        else:
            print('Copy: ./data/%s -> .results/%s/%s' % (sample_id, basename(fastq_file)))
            copy2(fastq_file, sample_dir)


if __name__ == '__main__':
    docopt(__doc__)
    main()
