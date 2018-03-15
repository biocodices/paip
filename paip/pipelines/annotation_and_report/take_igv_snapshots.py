import os
from os.path import join, basename

import luigi

from paip.task_types import SampleTask, ReportsTask, CohortTask
from paip.pipelines.variant_calling import (
    RecalibrateAlignmentScores,
    FilterGenotypes,
    ExtractSample,
    KeepReportableGenotypes,
)
from paip.helpers import (
    IGVScriptHelper,
    path_to_resource,
    X_server,
)


class GenerateReportsDone(ReportsTask, SampleTask, luigi.ExternalTask):
    """
    Class created to work as a reuquirement of tasks that come after the
    reports generation, but that don't need all the extra parameters
    that the report generation needs.
    """
    # This seems to be a cleaner solution than passing all of the
    # report-generation specific parameters around down to GenerateReports.
    def output(self):
        fn = join(self.dir, 'report_{}'.format(self.sample),
                  f'report_data__threshold_{self.min_reportable_category}.json')
        return luigi.LocalTarget(fn)


class TakeIGVSnapshots(ReportsTask, SampleTask):
    """
    Takes a snapshot of the pile of reads in IGV for each of the variants
    in a JSON file.
    """
    def requires(self):
        return {
            # GenerateReportsDone "fake" task needs the same params as TakeIGVSnapshots:
            'report_generation': GenerateReportsDone(**self.param_kwargs),

            # Other upstream tasks don't need the report-related params:
            'alignment': RecalibrateAlignmentScores(**self.sample_params()),
            'sample_all': ExtractSample(**self.sample_params()),
            'sample_reportable': KeepReportableGenotypes(**self.sample_params()),

            # The cohort required task needs a reduced version of the params:
            'cohort': FilterGenotypes(**self.cohort_params()),
        }

    def output(self):
        script = self.path('igv_batch_script')
        snapshots_dir = join(self.dir,
                             f'igv_snapshots_{self.min_reportable_category}')
        return {
            'script': luigi.LocalTarget(script),
            'snapshots_dir': luigi.LocalTarget(snapshots_dir),
        }

    def run(self):
        snapshots_dir = self.output()['snapshots_dir'].path
        os.makedirs(snapshots_dir, exist_ok=True)

        script_path = self.output()['script'].path
        self.write_script(script_path=script_path)

        # I'm using the PID as a hopefully available DISPLAY number!
        with X_server(os.getpid()) as screen_number:
            program_name = 'igv snapshots'
            program_options = {
                'DISPLAY': screen_number,
                'script_path': script_path,
            }
            self.run_program(program_name, program_options)

    def write_script(self, script_path):
        """
        Writes the IGV batch script at *script_path* to take a screenshot of
        the pile of reads for each variant in the variants JSON of the sample.
        """
        alignment_file = self.input()['alignment'].path
        variants_json = \
            self.input()['report_generation'].path

        script_helper = IGVScriptHelper(
            variants_json=variants_json,
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


class TakeIGVSnapshotsCohort(CohortTask, ReportsTask, luigi.WrapperTask):
    SAMPLE_REQUIRES = TakeIGVSnapshots
