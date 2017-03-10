import luigi

from paip.helpers import PipelineReseter


class ResetPipeline(luigi.Task):
    """
    Removes all files from a Pipeline except for the FASTQs and config YAMLs.
    """

    basedir = luigi.Parameter(default='.')
    dry_run = luigi.IntParameter(default=1)

    def run(self):
        reseter = PipelineReseter(self.basedir)
        reseter.reset_pipeline(dry_run=bool(int(self.dry_run)))

