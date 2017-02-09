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

from paip import software_name
from paip.helpers import logo, DB, VcfMunger, run_command
from paip.programs import trim_adapters, BWA, Picard, GATK
from paip.components import Cohort, Sample


class UnzipAndCoppyFastqs(luigi.ExternalTask):
    sample_id = luigi.Parameter()
    def output(self):
        sample = Sample(self.sample_id)
        return [luigi.LocalTarget(fn) for fn in sample.fastqs]


class TrimReads(luigi.Task):
    sample_id = luigi.Parameter()

    def requires(self):
        return UnzipAndCoppyFastqs(self.sample_id)

    def run(self):
        command = trim_adapters(*[target.fn for target in self.input()])
        # run_command(command, logfile=self.__class__.__name__.lower() + '.log')

    def output(self):
        self.sample = Sample(self.sample_id)
        return [luigi.LocalTarget(fn) for fn in self.sample.trimmed_fastqs]


class AlignReads(luigi.Task):
    sample_id = luigi.Parameter()
    def requires(self): return TrimReads(self.sample_id)
    def run(self):
        trimmed_fastqs = [target.fn for target in self.input()]
        BWA().align_to_reference(trimmed_fastqs)
    def output(self):
        sample = Sample(self.sample_id)
        return luigi.LocalTarget(sample.file('sam'))


class AddOrReplaceReadGroups(luigi.Task):
    sample_id = luigi.Parameter()
    def requires(self): return AlignReads(self.sample_id)

    def run(self):
        # Nasty hardcoding of biocodices-specific DB connection.
        # FIXME: think how to solve this in a general way.
        db = DB('lab_production')
        samples = db.table('NGS_MUESTRAS').set_index('SAMPLE_ID')
        library_id = samples.loc[self.sample_id]['LIB_ID']
        sequencer_run_id = samples.loc[self.sample_id]['NGS_ID']

        Picard().add_or_replace_read_groups(
            sam_path=self.requires().output().fn,
            sample_id=self.sample_id,
            sample_library_id=library_id,
            sequencer_run_id=sequencer_run_id,
            out_path=self.output().fn,
        )

    def output(self):
        sample = Sample(self.sample_id)
        return luigi.LocalTarget(sample.file('raw.bam'))


class RealignReads(luigi.Task):
    sample_id = luigi.Parameter()
    def requires(self): return AddOrReplaceReadGroups(self.sample_id)
    def run(self):
        vcf_munger = VcfMunger()
        raw_bam = self.requires().output().fn
        realigned_bam = vcf_munger.realign_reads_around_indels(raw_bam)
        vcf_munger.recalibrate_quality_scores(realigned_bam,
                                              out_path=self.output().fn)
    def output(self):
        self.sample = Sample(self.sample_id)
        return luigi.LocalTarget(self.sample.file('recalibrated.bam'))


class HaplotypeCall(luigi.Task):
    sample_id = luigi.Parameter()
    def requires(self): return RealignReads(self.sample_id)
    def run(self):
        recalibrated_bam = self.requires().output().fn
        # GATK().create_gvcf(recalibrated_bam, out_path=self.output().fn)
        GATK().genotype_given_alleles(recalibrated_bam,
                                      out_path=self.output().fn)
    def output(self):
        self.sample = Sample(self.sample_id)
        return luigi.LocalTarget(self.sample.file('raw_variants.g.vcf'))


class JointGenotyping(luigi.Task):
    base_dir = luigi.Parameter(default='.')
    def requires(self):
        for sample in self.cohort.samples:
            yield HaplotypeCall(sample.id)
    def run(self):
        gvcf_list = [task.output().fn for task in self.requires()]
        GATK().joint_genotyping(gvcf_list=gvcf_list, out_path=self.output().fn)
    def output(self):
        self.cohort = Cohort(self.base_dir)
        return luigi.LocalTarget(self.cohort.file('raw_variants.vcf'))


class HardFiltering(luigi.Task):
    base_dir = luigi.Parameter(default='.')
    def requires(self):
        return JointGenotyping(self.base_dir)
    def run(self):
        raw_vcf = self.requires().output().fn
        VcfMunger().hard_filtering(raw_vcf, out_path=self.output().fn)
    def output(self):
        cohort = Cohort(self.base_dir)
        return luigi.LocalTarget(cohort.file('filtered.vcf'))


class GenotypeFiltering(luigi.Task):
    base_dir = luigi.Parameter(default='.')
    def requires(self):
        return JointGenotyping(self.base_dir)
    def run(self):
        GATK().filter_genotypes(self.input().fn, out_path=self.outfile)
    def output(self):
        self.outfile = self.input().fn.replace('.vcf', '.geno.vcf')
        return luigi.LocalTarget(self.outfile)


class LimitRegions(luigi.Task):
    base_dir = luigi.Parameter(default='.')
    def requires(self):
        return GenotypeFiltering(self.base_dir)
    def run(self):
        VcfMunger().limit_regions(self.input().fn, out_path=self.outfile)
    def output(self):
        self.outfile = self.input().fn.replace('.vcf', '.lim.vcf')
        return luigi.LocalTarget(self.outfile)


class SnpEffAnnotation(luigi.Task):
    base_dir = luigi.Parameter(default='.')
    def requires(self): return LimitRegions(self.base_dir)
    def run(self):
        VcfMunger().annotate_with_snpeff(self.input().fn, out_path=self.outfile)
    def output(self):
        self.outfile = self.input().fn.replace('.vcf', '.Eff.vcf')
        return luigi.LocalTarget(self.outfile)


class VEPAnnotation(luigi.Task):
    base_dir = luigi.Parameter(default='.')
    def requires(self): return SnpEffAnnotation(self.base_dir)
    def run(self):
        VcfMunger().annotate_with_VEP(self.input().fn, out_path=self.outfile)
    def output(self):
        self.outfile = self.input().fn.replace('.vcf', '.VEP.vcf')
        return luigi.LocalTarget(self.outfile)


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
