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
    --tasks                     List available tasks to run.

    --sample-id SAMPLE_ID       Sample ID that must match the name
                                of a subdirectory of the current dir.
                                Use it for tasks that operate on a
                                *single sample*.

    --base-dir BASE_DIR         Base directory for the run, parent
                                of the 'data' directory with the
                                fastq files.
"""

import re
import sys
from docopt import docopt
from os.path import expanduser, join, dirname

import luigi
import coloredlogs

from paip import software_name
from paip.helpers import (
    SampleTask,
    run_command,
    generate_command,
    logo,
)


# We will generate all of the files for a given sample
# in a subdirectory with the name of that sample and with
# the sample name as a prefix:
#
# Sample-X
# |__ Sample-X.R1.fastq
# |__ Sample-X.R2.fastq
# |__ Sample-X.sam
# |__ Sample-X.bam
#


class CheckFastqs(luigi.ExternalTask, SampleTask):
    """
    Expects fastq files with forward and reverse reads of the same
    sample.
    """
    sample_id = luigi.Parameter()

    def output(self):
        fastqs = self.sample_paths(['R1.fastq', 'R2.fastq'])
        return [luigi.LocalTarget(fn) for fn in fastqs]


class TrimAdapters(luigi.Task, SampleTask):
    """
    Expects fastq files with forward and reverse reads of the same
    sample. Trims the adapters of those reads files and generates
    new fastq files.
    """
    sample_id = luigi.Parameter()

    def requires(self):
        return CheckFastqs(self.sample_id)

    def run(self):
        options = {
            'forward_reads': self.input()[0].fn,
            'reverse_reads': self.input()[1].fn,
            'forward_output': self.output()[0].fn,
            'reverse_output': self.output()[1].fn,
        }

        self.run_program('fastq-mcf', options)

    def output(self):
        trimmed_fastqs = self.sample_paths(['R1.trimmed.fastq',
                                            'R2.trimmed.fastq'])
        return [luigi.LocalTarget(fn) for fn in trimmed_fastqs]


class AlignToReference(luigi.Task, SampleTask):
    """
    Expects two files: forward and reverse reads of the same sample.
    It will use the reference genome defined in resources.yml to
    map the genes to genomic coordinates.

    Generates a .sam file with the raw alignments.
    """
    sample_id = luigi.Parameter()

    def requires(self):
        return TrimReads(self.sample_id)

    def run(self):
        program_options = {
            'forward_reads': self.input()[0].fn,
            'reverse_reads': self.input()[1].fn,
        }

        # BWA writes the aligned reads to STDOUT, so we capture that:
        stdout, _ = self.run_program('bwa', program_options, log_stdout=False)

        # And then we write that BWA output in the intended file:
        with open(self.output().fn, 'wb') as f:
            f.write(stdout)

    def output(self):
        target = self.sample_path('raw_alignment.sam')
        return luigi.LocalTarget(target)


class AddOrReplaceReadGroups(luigi.Task, SampleTask):
    """
    Expects a SAM file with aligned reads. Reads sequencing data from the
    working directory and runs a command that adds (or replaces) read groups
    to each read. The result is written to a BAM file.
    """
    sample_id = luigi.Parameter()

    def requires(self):
        return AlignToReference(self.sample_id)

    def run(self):
        # This step assumes that the pipeline is run from the *parent*
        # directory of the sample dir, where sequencing_data.yml will
        # be located:
        self.load_sample_data_from_yaml('sequencing_data.yml')

        program_options = {
            'input_sam': self.input().fn,
            'sample_id': self.id_in_sequencing,
            'library_id': self.library_id,
            'sequencing_id': self.sequencing_id,
            'platform_unit': self.platform_unit,
            'platform': self.platform,
            'output_bam': self.output().fn,
        }

        self.run_program('picard AddOrReplaceReadGroups', program_options)

    def output(self):
        fn = 'raw_alignment_with_read_groups.bam'
        return luigi.LocalTarget(self.sample_path(fn))


class CreateRealignmentIntervals(luigi.Task, SampleTask):
    """
    Expects a BAM file with mapped reads and runs a command to create an
    'intervals' file with the regions that should be realigned considering
    known human indels.
    """
    sample_id = luigi.Parameter()

    def requires(self):
        return AddOrReplaceReadGroups(self.sample_id)

    def run(self):
        program_options = {
            'input_bam': self.input().fn,
            'outfile': self.output().fn,
        }

        self.run_program('gatk RealignerTargetCreator', program_options)

    def output(self):
        filename = self.sample_path('realignment.intervals')
        return luigi.LocalTarget(filename)


class RealignAroundIndels(luigi.Task, SampleTask):
    """
    Expects a BAM file and an intervals file. Runs a command to realign the reads
    in those intervals and produce a new BAM file with the fixed alignments.
    """
    sample_id = luigi.Parameter()

    def requires(self):
        return [AddOrReplaceReadGroups(self.sample_id),
                CreateRealignmentIntervals(self.sample_id)]

    def run(self):
        program_options = {
            'input_bam': self.input()[0].fn,
            'targets_file': self.input()[1].fn,
            'output_bam': self.output().fn,
        }

        self.run_program('gatk IndelRealigner', program_options)

    def output(self):
        filename = self.sample_path('realignment.bam')
        return luigi.LocalTarget(filename)


class CreateRecalibrationTable(luigi.Task, SampleTask):
    """
    Expects a BAM file. Runs a command to create a plain text file with a table
    for the recalibration of the scores of each called base. The recalibration
    of scores is needed because of the previous realignment.
    """
    sample_id = luigi.Parameter()

    def requires(self):
        return RealignAroundIndels(self.sample_id)

    def run(self):
        program_options = {
            'input_bam': self.input().fn,
            'outfile': self.output().fn,
        }

        self.run_program('gatk BaseRecalibrator', program_options)

    def output(self):
        filename = self.sample_path('recalibration_table')
        return luigi.LocalTarget(filename)


class RecalibrateScores(luigi.Task, SampleTask):
    """
    Expects a BAM file and a recalibration table file generated by GATK
    BaseRecalibrator. Runs a command to produce a new BAM recalibrated
    base scores.
    """
    sample_id = luigi.Parameter()

    def requires(self):
        return [RealignAroundIndels(self.sample_id),
                CreateRecalibrationTable(self.sample_id)]

    def run(self):
        program_options = {
            'input_bam': self.input()[0].fn,
            'recalibration_table': self.input()[1].fn,
            'output_bam': self.output().fn,
        }

        self.run_program('gatk PrintReads', program_options)

    def output(self):
        filename = self.sample_path('recalibrated.bam')
        return luigi.LocalTarget(filename)


#  class HaplotypeCall(luigi.Task):
    #  sample_id = luigi.Parameter()
    #  def requires(self): return RealignReads(self.sample_id)
    #  def run(self):
        #  recalibrated_bam = self.requires().output().fn
        #  # GATK().create_gvcf(recalibrated_bam, out_path=self.output().fn)
        #  GATK().genotype_given_alleles(recalibrated_bam,
                                      #  out_path=self.output().fn)
    #  def output(self):
        #  self.sample = Sample(self.sample_id)
        #  return luigi.LocalTarget(self.sample.file('raw_variants.g.vcf'))


#  class JointGenotyping(luigi.Task):
    #  base_dir = luigi.Parameter(default='.')
    #  def requires(self):
        #  for sample in self.cohort.samples:
            #  yield HaplotypeCall(sample.id)
    #  def run(self):
        #  gvcf_list = [task.output().fn for task in self.requires()]
        #  GATK().joint_genotyping(gvcf_list=gvcf_list, out_path=self.output().fn)
    #  def output(self):
        #  self.cohort = Cohort(self.base_dir)
        #  return luigi.LocalTarget(self.cohort.file('raw_variants.vcf'))


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

    if arguments['--tasks']:
        print('\n'.join(list_classes(__file__)))
        sys.exit()

    print(logo())
    print('Welcome to {}! Starting the pipeline...\n'
          .format(software_name))

    print('Options in effect:')
    for k, v in arguments.items():
        if v:
            print(' {} {}'.format(k, v))
    print()

    try:
        set_luigi_logging()
        luigi.run()
    except luigi.task_register.TaskClassNotFoundException:
        print('No task with name "{}". Here are the available tasks:'
              .format(arguments['TASK']))
        luigi_classes = list_classes(__file__)
        print('\n' + '\n'.join(luigi_classes) + '\n')


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
    log_format = '[%(asctime)s] @%(hostname)s %(levelname)s %(message)s'
    coloredlogs.DEFAULT_LOG_FORMAT = log_format
    coloredlogs.install(level='INFO')


def list_classes(filepath):
    """Reads the filepath and returns the defined classes names."""
    with open(filepath, 'r') as f:
        tasks = [' * %s' % re.search('class (.+)\(', line).group(1)
                 for line in f.readlines() if line.startswith('class')]
    return tasks


if __name__ == '__main__':
    run_pipeline()
