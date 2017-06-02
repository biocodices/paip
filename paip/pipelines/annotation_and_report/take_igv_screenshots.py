import os
from os.path import join, basename

import luigi

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
    in a JSON file.
    """
    variants_json = luigi.Parameter()

    OUTPUT = 'igv_batch_script'

    def requires(self):
        cohort_params = self.param_kwargs.copy()
        del(cohort_params['sample'])

        sample_params = self.param_kwargs.copy()
        del(sample_params['variants_json'])

        return {
            'alignment': RecalibrateAlignmentScores(**sample_params),
            'cohort': FilterGenotypes(**cohort_params),
            'sample_all': ExtractSample(**sample_params),
            'sample_reportable': KeepReportableGenotypes(**sample_params),
        }

    def run(self):
        igv_snapshots_dir = join(self.dir, 'igv_snapshots')
        os.makedirs(igv_snapshots_dir, exist_ok=True)

        alignment_file = self.input()['alignment'].path
        template_data = {
            'sample_igv_snapshots_dir': igv_snapshots_dir,
            'sample_alignment': alignment_file,
            'sample_alignment_trackname': basename(alignment_file),
            'cohort_variants': self.input()['cohort'].path,
            'sample_all_variants': self.input()['sample_all'].path,
            'sample_reportable_variants': self.input()['sample_reportable'].path,
        }

        script_helper = IGVScriptHelper(
            variants_json=self.variants_json,
            template_path=path_to_resource('igv_batch_template'),
            template_data=template_data,
        )

        script_helper.write_script(out_path=self.output().path)

        # TODO: run the script!

