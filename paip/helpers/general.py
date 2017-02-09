from datetime import datetime
from shutil import move
import requests
import sys


def timestamp(sep=':', hour=True, date=False):
    template = '%H{0}%M{0}%S'.format(sep)
    if date:
        template = '%Y-%m-%d_{}'.format(template)
    return datetime.now().strftime(template)


def params_dict_to_str(params_dict):
    params = ['-{} {}'.format(k, v) for k, v in params_dict.items()]
    return ' '.join(params)


def rename_tempfile(outfile, extra_file_extension=None):
    move(outfile + '.temp', outfile)
    if extra_file_extension:
        extra_file = outfile + '.temp.{}'.format(extra_file_extension)
        move(extra_file, extra_file.replace('.temp', ''))


def restful_api_query(url):
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)

    if not response.ok:
        response.raise_for_status()
        sys.exit()

    return response.json()


def sample_log_filenames():
    return [
        'fastqc',
        'fastq-mcf',
        'bwa',
        'AddOrReplaceReadGroups',
        'RealignerTargetCreator',
        'IndelRealigner',
        'BaseRecalibrator',
        'PrintReads',
        'CollectAlignmentSummaryMetrics',
        'DiagnoseTargets',
        'HaplotypeCaller_gvcf',
        'bcftools_view_samples',
    ]


def cohort_log_filenames():
    return [
        'GenotypeGVCFs',
        'SelectVariants_indels',
        'SelectVariants_snps',
        'VariantFiltration_indels_filter',
        'VariantFiltration_snps_filter',
        'CombineVariants',
        'VariantFiltration_genotype_filter',
        'SnpEff',
        'VEP',
    ]


def logo():
    return """
      _________________________________
   ~~ |  _____  _______ _____  _____  | ~~
   ~~ | |_____] |_____|   |   |_____] | ~~
   ~~ | |       |     | __|__ |       | ~~
   ~~ |_______________________________| ~~

"""
