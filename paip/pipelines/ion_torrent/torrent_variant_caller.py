import os
from os.path import join, isfile

from paip.task_types import SampleTask
from paip.pipelines.ion_torrent import ReheaderBam
from paip.helpers.create_cohort_task import create_cohort_task


class TorrentVariantCaller(SampleTask):
    """
    Takes a BAM and generates a gzipped VCF, along with many auxiliary files.
    """
    REQUIRES = ReheaderBam
    OUTPUT = {
        'gzipped_vcf': 'vcf.gz',
        'gzipped_vcf_index': 'vcf.gz.tbi',
        'genome_gzipped_vcf': 'genome.vcf.gz',
        'genome_gzipped_vcf_index': 'genome.vcf.gz.tbi',
    }

    def run(self):
        program_name = 'variant_caller_pipeline.py'
        program_options = {
            'input_bam': self.input().path,
            'output_dir': self.dir,
        }
        self.run_program(program_name, program_options)

        files_to_rename = {
            'TSVC_variants.vcf.gz': 'gzipped_vcf',
            'TSVC_variants.vcf.gz.tbi': 'gzipped_vcf_index',
            'TSVC_variants.genome.vcf.gz': 'genome_gzipped_vcf',
            'TSVC_variants.genome.vcf.gz.tbi': 'genome_gzipped_vcf_index',
        }
        for old_fn, new_file_tag in files_to_rename.items():
            old_fp = join(self.dir, old_fn)
            new_fp = self.output()[new_file_tag].path
            os.rename(old_fp, new_fp)

        files_to_add_sample_prefix = [
            'black_listed.vcf',
            'depth.txt',
            'indel_assembly.vcf',
            'small_variants_filtered.vcf',
            'small_variants.vcf',
        ]
        for old_fn in files_to_add_sample_prefix:
            old_fp = join(self.dir, old_fn)
            new_fp = self.path(old_fn) # Just add the sample name as prefix
            if isfile(old_fp):
                os.rename(old_fp, new_fp)


TorrentVariantCallerCohort = create_cohort_task(TorrentVariantCaller)
