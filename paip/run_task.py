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
    paip (-T | --tasks)
    paip (-h | --help)

Examples:
    paip VariantCalling --basedir . --pipeline-type all_sites --min-dp 100
    paip VariantCalling --basedir Seq1 --pipeline-type target_sites --min-gq 30
    paip VariantCalling --pipeline-type target_sites --trim-software fastq-mcf
    paip QualityControl --basedir . --pipeline-type target_sites
    paip ResetPipeline [--basedir BASEDIR] [--dry-run BOOL]

Options:

    VariantCalling options
    ----------------------

    --basedir BASEDIR       Base directory for the run

                            (default=current directory).

    --pipeline-type TYPE    Pipeline type: 'variant_sites', 'target_sites' or
                            'all_sites'.

                            (default=variant_sites)

    --min-gq GQ             Minimum Genotype Quality (GQ) to use during
                            genotype filtering.

                            (default=30)

    --min-dp DP             Minimum read depth to use during genotype filtering.

                            (default=30)

    --trim-software NAME    Name of the software to use in the reads trimming
                            step. Options: 'cutadapt', 'fastq-mcf'.

                            (default=cutadapt)

    --samples SAMPLES       Samples to include in the Cohort. Pass a list of
                            comma-separated names like S1,S2,S3 to limit the
                            Cohort to those samples.

                            Use for Cohort tasks, in case you don't want to
                            include all samples in the pipeline.

                            (default=ALL)

    --sample SAMPLE         Sample ID that must match the name of a subdirectory
                            of the current dir.

                            Use for tasks that operate on a single sample. Not
                            needed for Cohort tasks.


    AnnotateVariants options
    ------------------------

    --cache CACHE           Options: 'mysq', 'postgres', 'redis', 'dict'. The
                            cache must be available! Check the `anotamela`
                            package for details about that.

                            (default='mysql')

    --http-proxy PROXY      HTTP proxy to use for AnnotateVariants. Typically,
                            you would set a Tor instance locally and use the
                            default value.

                            (default='socks5://localhost:9050')

    --annotation-kwargs JSON  Extra keyword arguments for AnnotateVariants,
                              which will be passed to `anotamela`'s
                              AnnotationPipeline. Pass them as a JSON
                              dictionary.

                              (default='{}')


    GenerateReports options
    -----------------------

    --templates-dir TPL_DIR    Directory with the Jinja templates for the HTML
                               report generation.

    --translations-dir TRANS_DIR     Directory with the translation files (.yml)
                                     with texts for the reports.

    --min-odds-ratio MIN_OR    Minimum odds ratio to consider a GWAS association
                               as reportable.

                               (default=1) Includes all associations.

    --max-frequency MAX_FR     Maximum allele frequency of an allele to be
                               reportable.

                               (default=1) Includes all alleles.

    --min-reportable-category MIN_CAT   Minimum category to consider an
                                        annotation as reportable. E.g. DRUG,
                                        ASSOC, LPAT, PAT.

                                        (default=DRUG)

    --phenos-regex-list PHENOS  Optional JSON string with the list of phenotype
                                patterns to keep in the report (removes any
                                allele info that is about a non-matching
                                phenotype). Patters are matched in case
                                insensitive mode. E.g.: "['cardi', 'myo']"

    --phenos-regex-file FILE    Optional file with one phenotype pattern to
                                keep per line (removes any allele info that is
                                about a non-matching phenotype).


    ResetPipeline options
    ---------------------

    --dry-run BOOL          If set as 1, it will print the files to delete, but
                            won't actually delete anything.

                            If set as 0, it deletes all files under the
                            directory, except: .fastq[.gz], .rb, .py, and .yml.

                            (default=1)


    General options
    ---------------------

    -T --tasks              List available tasks to run.

    --workers WORKERS       Number of parallel tasks to run.

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
