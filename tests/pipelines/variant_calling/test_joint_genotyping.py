import pytest

from paip.pipelines.variant_calling import JointGenotyping, MakeGVCF


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(JointGenotyping)


def test_requires(task):
    expected_dependencies = [MakeGVCF(sample='Sample1', basedir=task.basedir),
                             MakeGVCF(sample='Sample2', basedir=task.basedir)]
    assert task.requires() == expected_dependencies


def test_run(task, mock_rename):
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'GenomeAnalysisTK.jar -T GenotypeGVCFs' in command
    expected_inputs = ['-V {}'.format(input_[0].path)
                       for input_ in task.input()]
    assert ' '.join(expected_inputs) in command
    assert 'vcf-luigi-tmp' in command

    assert mock_rename.call_count == 2

