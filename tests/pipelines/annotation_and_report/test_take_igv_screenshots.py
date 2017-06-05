from unittest.mock import Mock

import pytest

import paip
from paip.helpers import IGVScriptHelper
from paip.pipelines.annotation_and_report import TakeIGVScreenshots


@pytest.fixture
def task(sample_task_factory):
    json = pytest.helpers.file('Cohort1/Sample1/Sample1_variants.records.json')
    return sample_task_factory(TakeIGVScreenshots,
                               extra_params={'variants_json': json})


def test_write_script(task, monkeypatch):
    mock_script_helper = Mock(name='IGVScriptHelper_instance',
                              spec=IGVScriptHelper)
    mock_script_helper_class = Mock(name='IGVScriptHelper',
                                    return_value=mock_script_helper)

    monkeypatch.setattr(paip.pipelines.annotation_and_report.take_igv_screenshots,
                        'IGVScriptHelper', mock_script_helper_class)

    script_path = '/path/to/script.txt'

    task.write_script(script_path=script_path)

    # Test how IGVScriptHelper class was initialized
    mock_script_helper_class.assert_called_once()
    init = mock_script_helper_class.call_args[1]
    init_tpl = init['template_data']
    assert init_tpl['sample_igv_snapshots_dir'].endswith('/igv_snapshots')
    assert init_tpl['cohort_variants'].endswith('.filt.geno_filt.vcf')
    assert init_tpl['sample_alignment'].endswith('.realignment_recalibrated.bam')
    assert init_tpl['sample_alignment_trackname'].endswith('.realignment_recalibrated.bam')
    assert init_tpl['sample_all_variants'].endswith('.with_filters.vcf')
    assert init_tpl['sample_reportable_variants'].endswith('.reportable.vcf')
    assert init_tpl['sample_reportable_variants'].endswith('.reportable.vcf')
    assert init['template_path'].endswith('igv_batch_template')
    assert init['variants_json'].endswith('variants.records.json')

    # Test how the script helper was used to write the IGV script
    mock_script_helper.write_script.assert_called_once()
    out_path = mock_script_helper.write_script.call_args[1]['out_path']
    assert out_path == script_path


def test_run(task, mock_makedirs):
    mock_write_script = Mock()
    task.write_script = mock_write_script

    task.run()

    mock_makedirs.assert_called_once()
    mock_makedirs.call_args[0][0].endswith('/igv_snapshots')
    assert mock_makedirs.call_args[1]['exist_ok']

    mock_write_script.assert_called_once_with(
        script_path=task.output()['script'].path
    )

    task.run_program
    (program_name, program_options), _ = task.run_program.call_args

    assert program_name == 'igv snapshots'
    assert program_options['DISPLAY'] == ':99'
    assert program_options['script_path'].endswith('igv_batch_script')


