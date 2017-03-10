import luigi


class ResetPipeline(luigi.Task):
    basedir = luigi.Parameter(default='.')
    dry_run = luigi.Parameter(default=1)

    def run(self):
        reseter = PipelineReseter(self.basedir)
        reseter.reset_pipeline()


