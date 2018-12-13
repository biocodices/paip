import pytest

from paip.pipelines.variant_calling import ExternalExome


def test_run(sample_task_factory):
    task = sample_task_factory(ExternalExome, sample_name='SampleWithExome')
    assert task.complete()

    task = sample_task_factory(ExternalExome, sample_name='SampleWithoutExome')
    assert not task.complete()
