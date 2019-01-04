import re
from paip.pipelines.variant_calling import TrimAdapters


def test_run(sample_task_factory):
    task = sample_task_factory(TrimAdapters)
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'cutadapt' in command
    assert task.input()['forward_reads'].path in command
    assert task.input()['reverse_reads'].path in command

    # This is important: cutadapt will only compress its output if it detects
    # filenames ending in ".gz", so we can't use different endings:
    assert re.search(r'Sample1.R1.trimmed.-luigi-tmp-\d+.fastq.gz ', command)
    assert re.search(r'Sample1.R2.trimmed.-luigi-tmp-\d+.fastq.gz ', command)
