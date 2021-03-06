import re

import pytest

from paip.pipelines.annotation import AnnotateWithCosmic
from paip.pipelines.report import ExtractSample


@pytest.fixture
def task(sample_task_factory):
    return sample_task_factory(ExtractSample,
                               sample_name='Sample1',
                               cohort_name='Cohort1')

def test_requires(task):
    assert isinstance(task.requires(), AnnotateWithCosmic)

def test_run(task, mock_rename):
    task.run()

    (command, ), kwargs = task.run_command.call_args

    assert 'GenomeAnalysisTK.jar -T SelectVariants'
    assert '--sample_name Sample1'
    assert re.search(r'-V .+Cohort1..+.vcf', command)

    assert re.search(r'.+Sample1..+.with_filters.vcf-luigi-tmp',
                     kwargs['redirect_stdout_to_path'])
    assert command.endswith(r" | grep -v '\./\.'")

    assert mock_rename.call_count == 1
