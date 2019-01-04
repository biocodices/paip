import os
from unittest.mock import Mock
from contextlib import contextmanager

import pytest

import paip
from paip.helpers import IGVScriptHelper
from paip.pipelines.annotation_and_report import TakeIGVSnapshots



@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(TakeIGVSnapshots,
                               extra_params={'min_reportable_category': 'PAT'})


def test_write_script(task, monkeypatch):
    mock_script_helper = Mock(name='IGVScriptHelper_instance',
                              spec=IGVScriptHelper)
    mock_script_helper_class = Mock(name='IGVScriptHelper',
                                    return_value=mock_script_helper)

    monkeypatch.setattr(paip.pipelines.annotation_and_report.take_igv_snapshots,
                        'IGVScriptHelper', mock_script_helper_class)

    script_path = '/path/to/script.txt'

    task.write_script(script_path=script_path)

    # Test how IGVScriptHelper class was initialized
    mock_script_helper_class.assert_called_once()
    init = mock_script_helper_class.call_args[1]
    init_tpl = init['template_data']
    assert init_tpl['sample_igv_snapshots_dir'].endswith('/igv_snapshots_PAT')
    assert init_tpl['cohort_variants'].endswith('.filt.geno_filt.vcf')
    assert init_tpl['sample_alignment'].endswith('.dupmarked_alignment.bam')
    assert init_tpl['sample_alignment_trackname'].endswith('.dupmarked_alignment.bam')
    assert init_tpl['sample_all_variants'].endswith('.with_filters.vcf')
    assert init_tpl['sample_reportable_variants'].endswith('.reportable.vcf')
    assert init_tpl['sample_reportable_variants'].endswith('.reportable.vcf')
    assert init['template_path'].endswith('igv_batch_template')
    assert init['variants_json'].endswith('report_data_threshold_PAT.json')

    # Test how the script helper was used to write the IGV script
    mock_script_helper.write_script.assert_called_once()
    out_path = mock_script_helper.write_script.call_args[1]['out_path']
    assert out_path == script_path


def test_run(task, mock_makedirs, monkeypatch):
    mock_write_script = Mock(return_value=None)
    task.write_script = mock_write_script

    # FIXME: This can probably be mocked in a better way
    @contextmanager
    def mock_X_server(port_number):
        mock_X_server.call_arg = port_number
        yield port_number

    monkeypatch.setattr(paip.pipelines.annotation_and_report.take_igv_snapshots,
                        'X_server', mock_X_server)

    task.run()

    assert mock_X_server.call_arg == os.getpid()

    mock_makedirs.assert_called_once()
    mock_makedirs.call_args[0][0].endswith('/igv_snapshots_PAT')
    assert mock_makedirs.call_args[1]['exist_ok']

    mock_write_script.assert_called_once_with(
        script_path=task.output()['script'].path
    )

    (command, ), kwargs = task.run_command.call_args

    assert 'igv.jar' in command
    assert command.startswith('DISPLAY=:')
    assert command.endswith('Sample1.igv_batch_script')
