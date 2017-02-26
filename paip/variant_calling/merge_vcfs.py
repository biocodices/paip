from paip.task_types import CohortTask
from paip.variant_calling import CallTargets


class MergeVCFs(CohortTask):
    """
    Take the single-sample VCF files from each sample in the target_sites
    pipeline and merge them into a multi-sample VCF.
    """
    OUTPUT = 'vcf'

    def requires(self):
        return [CallTargets(sample=sample, basedir=self.basedir)
                for sample in self.sample_list]

    def run(self):
        # CallTargets outputs both a VCF and a BAM (in that order).
        # We use the VCFs here:
        input_vcfs = ['-V {}'.format(inputs[0].fn) for inputs in self.input()]

        with self.output().temporary_path() as self.temp_vcf:
            program_name = 'gatk CombineVariants'
            program_options = {
                'input_vcfs': ' '.join(input_vcfs),
                'output_vcf': self.temp_vcf,
            }

            self.run_program(program_name, program_options)

        self.rename_temp_idx()

