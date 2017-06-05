import os
from os.path import join, basename, dirname, isfile

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

    def requires(self):
        cohort_params = self.param_kwargs.copy()
        del(cohort_params['sample'])
        del(cohort_params['variants_json'])

        sample_params = self.param_kwargs.copy()
        del(sample_params['variants_json'])

        return {
            'alignment': RecalibrateAlignmentScores(**sample_params),
            'cohort': FilterGenotypes(**cohort_params),
            'sample_all': ExtractSample(**sample_params),
            'sample_reportable': KeepReportableGenotypes(**sample_params),
        }

    def output(self):
        script = self.path('igv_batch_script')
        snapshots_dir = join(self.dir, 'igv_snapshots')
        return {
            'script': luigi.LocalTarget(script),
            'snapshots_dir': luigi.LocalTarget(snapshots_dir),
        }

    def run(self):
        snapshots_dir = self.output()['snapshots_dir'].path
        os.makedirs(snapshots_dir, exist_ok=True)

        script_path = self.output()['script'].path
        self.write_script(script_path=script_path)

        program_name = 'igv snapshots'
        program_options = {
            'DISPLAY': ':99',  # Assumes a big DISPLAY number won't be in use
            'script_path': script_path,
        }
        self.run_program(program_name, program_options)

    def write_script(self, script_path):
        """
        Writes the IGV batch script at *script_path* to take a screenshot of
        the pile of reads for each variant in the variants JSON of the sample.
        """
        alignment_file = self.input()['alignment'].path

        script_helper = IGVScriptHelper(
            variants_json=self.variants_json,
            template_path=path_to_resource('igv_batch_template'),
            template_data={
                'sample_igv_snapshots_dir': self.output()['snapshots_dir'].path,
                'sample_alignment': alignment_file,
                'sample_alignment_trackname': basename(alignment_file),
                'sample_reportable_variants': \
                    self.input()['sample_reportable'].path,
                'sample_all_variants': self.input()['sample_all'].path,
                'cohort_variants': self.input()['cohort'].path,
            }
        )

        script_helper.write_script(out_path=script_path)

