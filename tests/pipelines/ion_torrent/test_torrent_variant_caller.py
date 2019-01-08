import os
from unittest.mock import Mock

from paip.pipelines.ion_torrent import TorrentVariantCaller


def test_run(sample_task_factory, mock_rename, monkeypatch):
    mock_isfile = Mock(return_value=True)
    monkeypatch.setattr(os.path, 'isfile', mock_isfile)

    task = sample_task_factory(TorrentVariantCaller,
                               sample_name='Sample1',
                               cohort_name='IonCohort')
    task.run()
    (command, ), kwargs = task.run_command.call_args

    assert 'python2.7' in command
    assert 'variant_caller_pipeline.py' in command
    assert 'Sample1.fix.bam' in command

    assert mock_rename.call_count == 12
    assert mock_isfile.call_count == 6

    rename_call_args = mock_rename.call_args_list[0]
    assert 'TSVC_variants.vcf' in rename_call_args[0][0]
    assert 'Sample1.vcf' in rename_call_args[0][1]

    rename_call_args = mock_rename.call_args_list[1]
    assert 'TSVC_variants.vcf.gz' in rename_call_args[0][0]
    assert 'Sample1.vcf.gz' in rename_call_args[0][1]

    rename_call_args = mock_rename.call_args_list[2]
    assert 'TSVC_variants.vcf.gz.tbi' in rename_call_args[0][0]
    assert 'Sample1.vcf.gz.tbi' in rename_call_args[0][1]

    rename_call_args = mock_rename.call_args_list[3]
    assert 'TSVC_variants.genome.vcf' in rename_call_args[0][0]
    assert 'Sample1.g.vcf' in rename_call_args[0][1]

    rename_call_args = mock_rename.call_args_list[4]
    assert 'TSVC_variants.genome.vcf.gz' in rename_call_args[0][0]
    assert 'Sample1.g.vcf.gz' in rename_call_args[0][1]

    rename_call_args = mock_rename.call_args_list[5]
    assert 'TSVC_variants.genome.vcf.gz.tbi' in rename_call_args[0][0]
    assert 'Sample1.g.vcf.gz.tbi' in rename_call_args[0][1]

    rename_call_args = mock_rename.call_args_list[6]
    assert 'black_listed.vcf' in rename_call_args[0][0]
    assert 'black_listed.vcf' in mock_isfile.call_args_list[0][0][0]
    assert 'Sample1.black_listed.vcf' in rename_call_args[0][1]

    rename_call_args = mock_rename.call_args_list[7]
    assert 'depth.txt' in rename_call_args[0][0]
    assert 'depth.txt' in mock_isfile.call_args_list[1][0][0]
    assert 'Sample1.depth.txt' in rename_call_args[0][1]

    rename_call_args = mock_rename.call_args_list[8]
    assert 'indel_assembly.vcf' in rename_call_args[0][0]
    assert 'indel_assembly.vcf' in mock_isfile.call_args_list[2][0][0]
    assert 'Sample1.indel_assembly.vcf' in rename_call_args[0][1]

    rename_call_args = mock_rename.call_args_list[9]
    assert 'small_variants_filtered.vcf' in rename_call_args[0][0]
    assert 'small_variants_filtered.vcf' in mock_isfile.call_args_list[3][0][0]
    assert 'Sample1.small_variants_filtered.vcf' in rename_call_args[0][1]

    rename_call_args = mock_rename.call_args_list[10]
    assert 'small_variants.vcf' in rename_call_args[0][0]
    assert 'small_variants.vcf' in mock_isfile.call_args_list[4][0][0]
    assert 'Sample1.small_variants.vcf' in rename_call_args[0][1]

    rename_call_args = mock_rename.call_args_list[11]
    assert 'tvc_metrics.json' in rename_call_args[0][0]
    assert 'tvc_metrics.json' in mock_isfile.call_args_list[5][0][0]
    assert 'Sample1.tvc_metrics.json' in rename_call_args[0][1]
