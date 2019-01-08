from paip.task_types import CohortTask
from paip.pipelines.variant_calling import MakeGVCF
from paip.pipelines.ion_torrent import TorrentVariantCaller


class JointGenotyping(CohortTask):
    """
    Use the gVCF files from many samples to do a joint genotyping.
    Generates a multisample VCF.
    """
    OUTPUT = 'vcf'

    def requires(self):
        tasks = []
        for sample_name in self.sample_list:
            ion_sample = self.sequencing_data[sample_name].get('ion')
            sample_task_class = TorrentVariantCaller if ion_sample else MakeGVCF
            task = sample_task_class(sample=sample_name, basedir=self.basedir)
            tasks.append(task)
        return tasks

    def run(self):
        input_gvcfs = []

        for require in self.requires():
            if isinstance(require, MakeGVCF):
                # MakeGVCF outputs both a GVCF and a BAM (in that order),
                # we use the GVCF here:
                input_gvcfs.append(require.output()[0].path)
            elif isinstance(require, TorrentVariantCaller):
                input_gvcfs.append(require.output()['genome_vcf'].path)

        input_gvcfs_params = ['-V {}'.format(gvcf) for gvcf in input_gvcfs]

        with self.output().temporary_path() as self.temp_vcf:
            program_name = 'gatk3 GenotypeGVCFs ' + self.pipeline_type
            program_options = {
                'input_gvcfs': ' '.join(input_gvcfs_params),
                'output_vcf': self.temp_vcf
            }
            self.run_program(program_name, program_options)

        self.rename_temp_idx()
