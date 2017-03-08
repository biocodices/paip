import luigi

from paip.task_types import CohortTask
from paip.pipelines.variant_calling import MakeGVCF


class JointGenotyping(CohortTask):
    """
    Use the gVCF files from many samples to do a joint genotyping.
    Generates a multisample VCF.
    """
    def requires(self):
        return [MakeGVCF(sample=sample, basedir=self.basedir)
                for sample in self.sample_list]

    def run(self):
        # MakeGVCF outputs both a GVCF and a BAM (in that order).
        # We use the GVCFs here:
        input_vcfs = ['-V {}'.format(inputs[0].fn) for inputs in self.input()]

        with self.output().temporary_path() as self.temp_vcf:
            program_name = 'gatk GenotypeGVCFs ' + self.pipeline_type
            program_options = {
                'input_gvcfs': ' '.join(input_vcfs),
                'output_vcf': self.temp_vcf
            }

            self.run_program(program_name, program_options)

        self.rename_temp_idx()

    def output(self):
        return luigi.LocalTarget(self.cohort_path('vcf'))

