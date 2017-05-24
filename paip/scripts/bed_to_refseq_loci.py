#!/usr/bin/env python
"""
Converts the features found in a .bed file to the .refseq.loci format that
plinkseq would produce. Useful to avoid installing plinkseq if you already
have the genes by interval data.

Output goes to STDOUT.

Usage:
    bed_to_refseq_loci.py BEDFILE

For instance, the bed would look like this:

    1   100000  100100  GENE1
    2   100000  100100  GENE2

So the output would be generated like this:

    chr1:100000..100100 1   GENE1
    chr2:100000..100100 1   GENE2

"""

import re

from docopt import docopt


def main():
    arguments = docopt(__doc__)

    with open(arguments['BEDFILE']) as f:
        for line in f:
            field_names = 'chrom start end feature'.split()
            field_values = re.split(r'\s+', line.strip())
            row_info = dict(zip(field_names, field_values))

            # Assuming there's only one feature per interval
            new_line = 'chr{chrom}:{start}..{end} 1 {feature}'.format(**row_info)
            print(new_line)


if __name__ == '__main__':
    main()
