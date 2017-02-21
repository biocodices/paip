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

                            Use for Cohort tasks.

    --samples SAMPLES       Samples to include in the Cohort
                            (defaults to ALL samples found in
                            the --basedir). Pass a list of
                            comma-separated names like
                            S1,S2,S3 to limit the Cohort to
                            those samples.

                            Use for Cohort tasks.

    --pipeline-type TYPE    Pipeline type: 'variant_sites',
                            'target_sites' or 'all_sites'.

    --workers WORKERS       Number of parallel tasks to run.
                            Defaults to 1.

"""

import sys
from docopt import docopt
from os.path import expanduser, join, dirname

import luigi
import logging
import coloredlogs

from paip import software_name
from paip.pipeline import *


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


#  class HardFiltering(luigi.Task):
    #  base_dir = luigi.Parameter(default='.')
    #  def requires(self):
        #  return JointGenotyping(self.base_dir)
    #  def run(self):
        #  raw_vcf = self.requires().output().fn
        #  VcfMunger().hard_filtering(raw_vcf, out_path=self.output().fn)
    #  def output(self):
        #  cohort = Cohort(self.base_dir)
        #  return luigi.LocalTarget(cohort.file('filtered.vcf'))


#  class GenotypeFiltering(luigi.Task):
    #  base_dir = luigi.Parameter(default='.')
    #  def requires(self):
        #  return JointGenotyping(self.base_dir)
    #  def run(self):
        #  GATK().filter_genotypes(self.input().fn, out_path=self.outfile)
    #  def output(self):
        #  self.outfile = self.input().fn.replace('.vcf', '.geno.vcf')
        #  return luigi.LocalTarget(self.outfile)


#  class LimitRegions(luigi.Task):
    #  base_dir = luigi.Parameter(default='.')
    #  def requires(self):
        #  return GenotypeFiltering(self.base_dir)
    #  def run(self):
        #  VcfMunger().limit_regions(self.input().fn, out_path=self.outfile)
    #  def output(self):
        #  self.outfile = self.input().fn.replace('.vcf', '.lim.vcf')
        #  return luigi.LocalTarget(self.outfile)


#  class SnpEffAnnotation(luigi.Task):
    #  base_dir = luigi.Parameter(default='.')
    #  def requires(self): return LimitRegions(self.base_dir)
    #  def run(self):
        #  VcfMunger().annotate_with_snpeff(self.input().fn, out_path=self.outfile)
    #  def output(self):
        #  self.outfile = self.input().fn.replace('.vcf', '.Eff.vcf')
        #  return luigi.LocalTarget(self.outfile)


#  class VEPAnnotation(luigi.Task):
    #  base_dir = luigi.Parameter(default='.')
    #  def requires(self): return SnpEffAnnotation(self.base_dir)
    #  def run(self):
        #  VcfMunger().annotate_with_VEP(self.input().fn, out_path=self.outfile)
    #  def output(self):
        #  self.outfile = self.input().fn.replace('.vcf', '.VEP.vcf')
        #  return luigi.LocalTarget(self.outfile)

def run_pipeline():
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
            logger.info(' {:<13} -> {:20} '.format(k, v))

    try:
        luigi.run()
    except luigi.task_register.TaskClassNotFoundException:
        available_tasks = '\n'.join(list_tasks())
        logger.info('No task with named "{}". '
                    'Available tasks are:\n\n{}\n'
                    .format(arguments['TASK'], available_tasks))


def set_luigi_logging():
    config_file = join(dirname(dirname(__file__)), 'example_config',
                       'luigi_logging.conf')

    # For luigi's interface see:
    # http://luigi.readthedocs.io/en/stable/api/luigi.interface.html
    luigi.interface.setup_interface_logging(
        conf_file=expanduser(config_file)
    )
    # ^ Here I replace luigi's default logger config with a custom
    # file. The details of that file are not relevant anyway,
    # because the actual log config will come from coloredlogs below:
    log_format = '[%(asctime)s] @%(hostname)s %(message)s'
    coloredlogs.DEFAULT_LOG_FORMAT = log_format
    coloredlogs.install(level='INFO')


def list_tasks():
    """List all luigi tasks available."""
    import paip
    return [name for name, obj in paip.pipeline.__dict__.items()
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
    run_pipeline()
