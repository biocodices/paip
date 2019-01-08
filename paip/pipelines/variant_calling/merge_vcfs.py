from paip.task_types import CohortTask
from paip.pipelines.variant_calling import ResetFilters
from paip.pipelines.ion_torrent import TorrentVariantCaller


class MergeVCFs(CohortTask):
    """
    Take the single-sample VCF files from each sample in the target_sites
    pipeline or in the IonTorrent pipeline and merge them into a multi-sample
    VCF.
    """
    OUTPUT = 'vcf'

    def requires(self):
        tasks = []
        for sample_name in self.sample_list:
            ion_sample = self.sequencing_data[sample_name].get('ion')
            sample_task_class = TorrentVariantCaller if ion_sample else ResetFilters
            task = sample_task_class(sample=sample_name, basedir=self.basedir)
            tasks.append(task)
        return tasks

    def run(self):
        input_vcfs = []

        for require in self.requires():
            if isinstance(require, ResetFilters):
                input_vcfs.append(require.output().path)
            elif isinstance(require, TorrentVariantCaller):
                input_vcfs.append(require.output()['vcf'].path)

        input_vcfs_params = ['-V {}'.format(vcf) for vcf in input_vcfs]

        with self.output().temporary_path() as self.temp_vcf:
            program_name = 'gatk3 CombineVariants'
            program_options = {
                'input_vcfs': ' '.join(input_vcfs_params),
                'output_vcf': self.temp_vcf,
            }

            self.run_program(program_name, program_options)

        self.rename_temp_idx()
