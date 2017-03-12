#!/usr/bin/env python3.5

import logging
import sys

import luigi
import click

from paip import software_name
from paip.helpers import set_luigi_logging, list_tasks


logger = logging.getLogger('paip')


@click.group()
def cli():
    pass


@click.command('list')
def show_tasks():
    """List all pipeline tasks available."""

    for task_group_name, tasks in list_tasks().items():
        click.echo(' --- {} ---'.format(task_group_name))
        click.echo()
        for task_name, obj in sorted(tasks):
            if isinstance(obj, luigi.task_register.Register):
                click.echo('  *  {}'.format(task_name))
        click.echo()


#  @click.command('reset_pipeline')
#  @click.option('--basedir', help='Base directory for the run', default='.')
#  @click.option('--dry-run', help="Don't delete any files.", default=True)
#  def reset_pipeline(basedir, dry_run):
    #  ResetPipeline(basedir=basedir, dry_run=dry_run)


@click.command('run')
@click.option('--sample', help='ID/name of a sample in this cohort')
@click.option('--basedir', help='Base directory for the run', default='.')
@click.option('--pipeline-type',
              help='Options: variant_sites, target_sites, all_sites',
              default='target_sites')
@click.option('--min-gq', help='Minimum Genotype Quality', default=30)
@click.option('--min-dp', help='Minimum [Read] Depth', default=30)
@click.option('--trim-software', help='Options: cutadapt, fastq-mcf',
              default='cutadapt')
@click.argument('task_name', required=True)
def run_task(task_name, **kwargs):
    """Run a given pipeline task."""
    set_luigi_logging()

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

    click.echo(logo())
    logger.info('Welcome to {}! Starting the pipeline...'
                .format(software_name))

    logger.info('Options in effect:')
    for k, v in kwargs.items():
        if v:
            logger.info(' {} -> {} '.format(k, v))

    try:
        luigi.run()
    except luigi.task_register.TaskClassNotFoundException:
        logger.info('No task found with name "{}"'.format(task_name))
        list_tasks()
        sys.exit()


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


cli.add_command(run_task)
cli.add_command(list_tasks)


if __name__ == '__main__':
    cli()

