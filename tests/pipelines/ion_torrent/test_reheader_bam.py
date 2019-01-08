from unittest.mock import Mock
import pytest
from paip.pipelines.ion_torrent import ReheaderBam


def test_fix_header_sam(sample_task_factory, tmpdir):
    in_header = pytest.helpers.file('wrong_header.sam')
    out_header = tmpdir.join('fixed_header.sam')

    task = sample_task_factory(ReheaderBam, sample_name='Sample1')
    task.fix_header_sam(in_header, out_header)

    with open(out_header) as f:
        content = f.read()

    assert 'SM:Lib 1' not in content
    assert "@RG\tID:RGID\tCN:RGCN\tDT:RGDT\tFO:RGFO\tKS:RGKS\tPG:RGPG\tPL:RGPL\tPU:RGPU\tSM:Sample1\n" in content

    assert 'LN:16569' not in content
    # assert "LN:16571\n" in content

    assert 'SN:chr1' not in content
    assert 'SN:chrY' not in content
    assert 'SN:1' in content
    assert 'SN:Y' in content


def test_run(sample_task_factory, monkeypatch):
    mock_fix_header_sam = Mock()
    monkeypatch.setattr(ReheaderBam, 'fix_header_sam', mock_fix_header_sam)

    task = sample_task_factory(ReheaderBam,
                               sample_name='Sample1',
                               cohort_name='IonCohort')
    task.run()

    (command, ), kwargs = task.run_command.call_args_list[0]
    assert 'samtools view -H' in command
    assert 'Sample1.ion.bam' in command

    assert kwargs['redirect_stdout_to_path'].endswith('.header.sam')

    assert mock_fix_header_sam.call_count == 1

    (command, ), kwargs = task.run_command.call_args_list[1]

    assert 'samtools reheader' in command
    assert '.fix.bam-luigi' in kwargs['redirect_stdout_to_path']
