import os
from os.path import join, basename

from paip.task_types import SampleTask
from paip.pipelines.variant_calling import (
    RecalibrateAlignmentScores,
    FilterGenotypes,
    ExtractSample,
    KeepReportableGenotypes,
)
from paip.helpers import (
    IGVScriptHelper,
    path_to_resource,
)


class TakeIGVScreenshots(SampleTask):
    """
    Takes a screenshot of the pile of reads in IGV for each of the variants
    in a sample VCF.
    """
    OUTPUT = 'igv_batch_script'

    def requires(self):
        cohort_params = self.param_kwargs.copy()
        del(cohort_params['sample'])

        return [
            RecalibrateAlignmentScores(**self.param_kwargs),
            FilterGenotypes(**cohort_params),
            ExtractSample(**self.param_kwargs),
            KeepReportableGenotypes(**self.param_kwargs),
        ]

    def run(self):
        igv_snapshots_dir = join(self.dir, 'igv_snapshots')
        os.makedirs(igv_snapshots_dir, exist_ok=True)

        input_bam = self.input()[0].path
        input_vcf = self.input()[3].path

        template_data = {
            'sample_igv_snapshots_dir': igv_snapshots_dir,
            'sample_alignment': input_bam,
            'sample_alignment_trackname': basename(input_bam),
            'cohort_variants': self.input()[1].path,
            'sample_all_variants': self.input()[2].path,
            'sample_reportable_variants': input_vcf,
        }

        script_helper = IGVScriptHelper(
            vcf=input_vcf,
            template_path=path_to_resource('igv_batch_template'),
            template_data=template_data,
        )

        script_helper.write_script(out_path=self.output().path)

