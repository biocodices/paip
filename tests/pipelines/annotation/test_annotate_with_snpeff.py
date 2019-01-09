from unittest.mock import mock_open, patch
from paip.pipelines.annotation import AnnotateWithSnpeff


def test_run(sample_task_factory):
    task = sample_task_factory(AnnotateWithSnpeff)
    open_ = mock_open()

    # FIXME: this whole 'path' to the module hardcoding is ugly, but I need
    # the regular builtin open() to be operational for the rest of the code:
    with patch('paip.pipelines.annotation.annotate_with_snpeff.open', open_):
        task.run()

    (command, ), kwargs = task.run_command.call_args
    assert 'snpEff.jar ann' in command
    assert 'snpEff.summary.csv' in command
    assert command.endswith('Sample1.reportable.vcf')
    assert kwargs['log_stdout'] is False

    open_().write.assert_called_once_with(b'stdout')
    assert task.output().path.endswith('.eff.vcf')
