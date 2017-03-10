from unittest.mock import MagicMock

import pytest

import paip
from paip.pipelines import ResetPipeline


def test_run(monkeypatch):
    reset_pipeline = MagicMock()
    monkeypatch.setattr(paip.pipelines.reset_pipeline.PipelineReseter,
                        'reset_pipeline', reset_pipeline)
    basedir = pytest.helpers.file('Cohort1')

    task = ResetPipeline(basedir=basedir, dry_run=1)
    task.run()
    assert reset_pipeline.call_count == 1
    assert reset_pipeline.call_args[1] == {'dry_run': True}

    task = ResetPipeline(basedir=basedir, dry_run=0)
    task.run()
    assert reset_pipeline.call_count == 2  # 1 + the previous call
    assert reset_pipeline.call_args[1] == {'dry_run': False}

