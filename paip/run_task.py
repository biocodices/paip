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

Options:
    --tasks                 List available tasks to run.

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

    --min-gq                Minimum Genotype Quality (GQ) to
                            use during genotype filtering.
                            (default=30)

    --min-dp                Minimum read depth to use during
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

"""

import sys
from docopt import docopt
from os.path import expanduser, join, dirname
from os import environ

import luigi
import logging
import coloredlogs

from paip import software_name
from paip.pipelines.variant_calling import *
from paip.pipelines.quality_control import *
from paip.pipelines.variant_calling_task import VariantCalling
from paip.pipelines.quality_control_task import QualityControl
from paip.pipelines.annotate_variants import AnnotateVariants


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
        for task in list_tasks():
            print(' * ' + task)

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
        available_tasks = '\n'.join(list_tasks())
        logger.info('No task found with name "{}". '
                    'Available tasks are:\n\n{}\n'
                    .format(arguments['TASK'], available_tasks))


def set_luigi_logging():
    basedir = dirname(__file__)
    config_file = join(basedir, 'example_config', 'luigi_logging.conf')

    # Docs for luigi interface:
    # http://luigi.readthedocs.io/en/stable/api/luigi.interface.html
    luigi.interface.setup_interface_logging(
        conf_file=expanduser(config_file)
    )
    # ^ Here I replace luigi's default logger config with a custom
    # file. The details of that file are not relevant really,
    # because the actual log config will come from coloredlogs below.
    # But stepping over luigi's logger config like that is necessary
    # because otherwise I get duplicated logging output.
    log_format = '[%(asctime)s] @%(hostname)s %(message)s'
    coloredlogs.DEFAULT_LOG_FORMAT = log_format
    coloredlogs.install(level=environ.get('LOG_LEVEL') or 'INFO')


def list_tasks():
    """List all luigi tasks available."""
    import paip
    items = (list(paip.variant_calling.__dict__.items()) +
             list(paip.quality_control.__dict__.items()))
    return [name for name, obj in items
            if isinstance(obj, luigi.task_register.Register)]


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
