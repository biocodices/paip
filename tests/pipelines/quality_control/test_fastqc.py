from paip.pipelines.quality_control import FastQC


def test_run(sample_task_factory):
    task = sample_task_factory(FastQC)
    task.run()

    assert task.run_command.call_count == 2

    (command, ), kwargs = task.run_command.call_args_list[0]

    assert 'fastqc' in command
    assert task.input()['raw_reads']['forward_reads'].path in command
    assert task.input()['raw_reads']['reverse_reads'].path in command

    (command, ), kwargs = task.run_command.call_args_list[1]

    assert 'fastqc' in command
    assert task.input()['trimmed_reads']['forward_reads'].path in command
    assert task.input()['trimmed_reads']['reverse_reads'].path in command
