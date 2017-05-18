#!/usr/bin/env python3.5
"""

 .########.....###....####.########.
 .##.....##...##.##....##..##.....##
 .##.....##..##...##...##..##.....##
 .########..##.....##..##..########.
 .##........#########..##..##.......
 .##........##.....##..##..##.......
 .##........##.....##.####.##.......

Usage:
    paip TASK [options]
    paip --tasks
    paip (-h | --help)

Examples:
    paip VariantCalling --basedir . --pipeline-type all_sites --min-dp 100
    paip VariantCalling --basedir Seq1 --pipeline-type target_sites --min-gq 30
    paip VariantCalling --pipeline-type target_sites --trim-software fastq-mcf
    paip QualityControl --basedir . --pipeline-type target_sites
    paip ResetPipeline [--basedir BASEDIR] [--dry-run BOOL]

Options:
    -T --tasks              List available tasks to run.

    --sample SAMPLE         Sample ID that must match the name
                            of a subdirectory of the current dir.

                            Use for tasks that operate on a
                            single sample.

    --basedir BASEDIR       Base directory for the run
                            (default=current directory).

    --samples SAMPLES       Samples to include in the Cohort.
                            Pass a list of comma-separated names
                            like S1,S2,S3 to limit the Cohort to
                            those samples.
                            (default=ALL)

                            Use for Cohort tasks.

    --pipeline-type TYPE    Pipeline type: 'variant_sites',
                            'target_sites' or 'all_sites'.
                            (default=variant_sites)

    --min-gq GQ             Minimum Genotype Quality (GQ) to
                            use during genotype filtering.
                            (default=30)

    --min-dp DP             Minimum read depth to use during
                            genotype filtering.
                            (default=30)

    --trim-software NAME    Name of the software to use in the
                            reads trimming step. Options:
                            'cutadapt' (default), 'fastq-mcf'.

    --workers WORKERS       Number of parallel tasks to run.
                            (default=1)

    --cache CACHE           Name of a cache for AnnotateVariants.
                            Options: 'mysq', 'postgres',
                            'redis', 'dict'.
                            (default='mysql')

    --http-proxy PROXY      HTTP proxy to use for AnnotateVariants.
                            Typically, you would set a Tor instance
                            and use the default value.
                            (default='socks5://localhost:9050')

    --annotation-kwargs JSON   Extra keyword arguments for
                               AnnotateVariants, which will be
                            passed to anotamela's AnnotationPipeline.
                            Pass them as a JSON dictionary.
                            (default='{}')

    --dry-run BOOL          Argument for ResetPipeline, if set
                            as 1, it will not delete any files,
                            if set as 0, it will.
                            (default=1)

"""

import sys
from docopt import docopt

import luigi
import logging

from paip import software_name
from paip.helpers import set_luigi_logging
from paip.helpers.list_tasks import list_tasks


logger = logging.getLogger('paip')


# We will assume that for each sample there's a subdirectory
# with the sample's name and their files, prefixed with the
# same name. Cohort files will be put in the root directory
# of the cohort:
#
# Cohort-1
# |
# |—— Sample-X
# |   |—— Sample-X.R1.fastq
# |   |—— Sample-X.R2.fastq
# |
# |—— Sample-Y
# |   |—— Sample-Y.R1.fastq
# |   |—— Sample-Y.R2.fastq
# |
# |—— raw_genotypes.vcf
# |—— raw_genotypes.vcf.idx
#


def run_task():
    arguments = docopt(__doc__, version=software_name)
    set_luigi_logging()

    if arguments['--tasks']:
        for task_group_name, tasks in list_tasks().items():
            print(' --- {} ---'.format(task_group_name))
            print()
            for task_name, obj in sorted(tasks):
                if isinstance(obj, luigi.task_register.Register):
                    print('  *  {}'.format(task_name))
            print()
        sys.exit()

    logger.info('\n' + logo())
    logger.info('Welcome to {}! Starting the pipeline...'
                .format(software_name))

    logger.info('Options in effect:')
    for k, v in arguments.items():
        if v:
            logger.info(' {:<20} -> {:20} '.format(k, v))

    try:
        luigi.run()
    except luigi.task_register.TaskClassNotFoundException:
        logger.info('No task found with name "{}". '
                    'Run paip --tasks to list the available tasks'
                    .format(arguments['TASK']))


def logo():
    return """

 .########.....###....####.########.
 .##.....##...##.##....##..##.....##
 .##.....##..##...##...##..##.....##
 .########..##.....##..##..########.
 .##........#########..##..##.......
 .##........##.....##..##..##.......
 .##........##.....##.####.##.......

"""

if __name__ == '__main__':
    run_task()
