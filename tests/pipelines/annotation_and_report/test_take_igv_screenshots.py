import os
from unittest.mock import Mock

import pytest

import paip
from paip.pipelines.annotation_and_report import TakeIGVScreenshots


@pytest.fixture
def task(sample_task_factory):
    json = pytest.helpers.file('Cohort1/Sample1/Sample1_variants.records.json')
    return sample_task_factory(TakeIGVScreenshots,
                               extra_params={'variants_json': json})


def test_run(task, monkeypatch):
    makedirs = Mock()
    instance = Mock()
    IGVScriptHelper = Mock(return_value=instance)

    monkeypatch.setattr(os, 'makedirs', makedirs)
    monkeypatch.setattr(paip.pipelines.annotation_and_report.take_igv_screenshots,
                        'IGVScriptHelper', IGVScriptHelper)

    task.run()

    IGVScriptHelper.assert_called_once()
    init = IGVScriptHelper.call_args[1]
    init_tpl = init['template_data']
    assert init_tpl['sample_igv_snapshots_dir'].endswith('/igv_snapshots')
    assert init_tpl['cohort_variants'].endswith('.filt.geno_filt.vcf')
    assert init_tpl['sample_alignment'].endswith('.realignment_recalibrated.bam')
    assert init_tpl['sample_alignment_trackname'].endswith('.realignment_recalibrated.bam')
    assert init_tpl['sample_all_variants'].endswith('.with_filters.vcf')
    assert init_tpl['sample_reportable_variants'].endswith('.reportable.vcf')
    assert init_tpl['sample_reportable_variants'].endswith('.reportable.vcf')
    assert init['template_path'].endswith('/igv_batch_template')
    assert init['vcf'].endswith('.reportable.vcf')

    instance.write_script.assert_called_once()
    assert instance.write_script.call_args[1]['out_path'].endswith('.igv_batch_script')

    makedirs.assert_called_once()
    assert makedirs.call_args[0][0].endswith('/igv_snapshots')
    assert makedirs.call_args[1]['exist_ok']

