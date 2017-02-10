#!/usr/bin/env python3.5
"""
      _________________________________
   ~~ |  _____  _______ _____  _____  | ~~
   ~~ | |_____] |_____|   |   |_____] | ~~
   ~~ | |       |     | __|__ |       | ~~
   ~~ |_______________________________| ~~

Usage:
    paip TASK [options]
    paip --tasks
    paip (-h | --help)

Options:
    --tasks                             List available tasks to run.
    --sample-id SAMPLE_ID               Sample ID that must match the name
                                        of a subdirectory of the cwd. For tasks
                                        that operate on a single sample.
                                        Not needed for Cohort tasks.
    --base-dir BASE_DIR                 Base directory for the run, parent
                                        of the 'data' directory with the
                                        fastq files.
"""

import re
import sys
from docopt import docopt
import luigi
from os.path import join

from paip import software_name
from paip.helpers import (
    Sample,
    run_command,
    logo,
)
# , logo, DB, VcfMunger
from paip.pipeline import (
    trim_adapters,
    align_to_reference,
)
# from paip.programs import BWA, Picard, GATK
# from paip.components import Cohort


class CheckFastqs(luigi.ExternalTask):
    # From the start, we will assume that all files for a given sample
    # will be located in a subdirectory with the name of the sample:
    #
    # Sample-X
    # |__ Sample-X.R1.fastq
    # |__ Sample-X.R2.fastq
    #
    sample_id = luigi.Parameter()

    def output(self):
        fastq_filepaths = Sample(self.sample_id).paths(['{}.R1.fastq',
                                                        '{}.R2.fastq'])

        return [luigi.LocalTarget(fn) for fn in fastq_filepaths]


class TrimReads(luigi.Task):
    sample_id = luigi.Parameter()

    def requires(self):
        return CheckFastqs(self.sample_id)

    def run(self):
        fwd_reads, rev_reads = [target.fn for target in self.input()]
        command = trim_adapters(forward_reads=fwd_reads,
                                reverse_reads=rev_reads)

        log_filename = Sample(self.sample_id).path('{}.log.trim_reads')
        run_command(command, logfile=log_filename)

    def output(self):
        targets = Sample(self.sample_id).paths(['{}.R1.trimmed.fastq',
                                                '{}.R2.trimmed.fastq'])

        return [luigi.LocalTarget(fn) for fn in targets]


class AlignToReference(luigi.Task):
    sample_id = luigi.Parameter()

    def requires(self):
        return TrimReads(self.sample_id)

    def run(self):
        fwd_reads, rev_reads = [target.fn for target in self.input()]
        command = align_to_reference(forward_reads=fwd_reads,
                                     reverse_reads=rev_reads)
        log_filename = Sample(self.sample_id).path('{}.log.align_to_reference')

        # BWA writes the aligned reads to STDOUT, so we capture that:
        stdout, _ = run_command(command, logfile=log_filename,
                                log_stdout=False)

        # And then we write that BWA output in the intended file:
        with open(self.output().fn, 'wb') as f:
            f.write(stdout)

    def output(self):
        target = Sample(self.sample_id).path('{}.sam')
        return luigi.LocalTarget(target)


#  class AddOrReplaceReadGroups(luigi.Task):
    #  sample_id = luigi.Parameter()
    #  def requires(self): return AlignReads(self.sample_id)

    #  def run(self):
        #  # Nasty hardcoding of biocodices-specific DB connection.
        #  # FIXME: think how to solve this in a general way.
        #  db = DB('lab_production')
        #  samples = db.table('NGS_MUESTRAS').set_index('SAMPLE_ID')
        #  library_id = samples.loc[self.sample_id]['LIB_ID']
        #  sequencer_run_id = samples.loc[self.sample_id]['NGS_ID']

        #  Picard().add_or_replace_read_groups(
            #  sam_path=self.requires().output().fn,
            #  sample_id=self.sample_id,
            #  sample_library_id=library_id,
            #  sequencer_run_id=sequencer_run_id,
            #  out_path=self.output().fn,
        #  )

    #  def output(self):
        #  sample = Sample(self.sample_id)
        #  return luigi.LocalTarget(sample.file('raw.bam'))


#  class RealignReads(luigi.Task):
    #  sample_id = luigi.Parameter()
    #  def requires(self): return AddOrReplaceReadGroups(self.sample_id)
    #  def run(self):
        #  vcf_munger = VcfMunger()
        #  raw_bam = self.requires().output().fn
        #  realigned_bam = vcf_munger.realign_reads_around_indels(raw_bam)
        #  vcf_munger.recalibrate_quality_scores(realigned_bam,
                                              #  out_path=self.output().fn)
    #  def output(self):
        #  self.sample = Sample(self.sample_id)
        #  return luigi.LocalTarget(self.sample.file('recalibrated.bam'))


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
        luigi.run()
    except luigi.task_register.TaskClassNotFoundException:
        print('No task with name "{}". Here are the available tasks:'
              .format(arguments['TASK']))
        luigi_classes = list_classes(__file__)
        print('\n' + '\n'.join(luigi_classes) + '\n')


def list_classes(filepath):
    """Reads the filepath and returns the defined classes names."""
    with open(filepath, 'r') as f:
        tasks = [' * %s' % re.search('class (.+)\(', line).group(1)
                 for line in f.readlines() if line.startswith('class')]
    return tasks


if __name__ == '__main__':
    run_pipeline()
