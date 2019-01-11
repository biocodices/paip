from unittest.mock import Mock

import re

import pytest
import pandas as pd

from paip.pipelines.annotation import AnnotateWithCosmic


@pytest.fixture
def task(cohort_task_factory):
    return cohort_task_factory(AnnotateWithCosmic)

def test_run(task, monkeypatch):
    mock_add_COSMIC_INFO = Mock()
    monkeypatch.setattr(AnnotateWithCosmic, 'add_COSMIC_INFO',
                        mock_add_COSMIC_INFO)

    task.run()
    (command, ), kwargs = task.run_command.call_args
    assert 'SnpSift.jar annotate -id -noInfo -v' in command
    assert re.search(r'Cohort1..+.COS-temp.vcf',
                     kwargs['redirect_stdout_to_path'])

    _args = mock_add_COSMIC_INFO.call_args[0]
    assert _args[0].endswith('COS-temp.vcf')
    assert re.search(r'Cohort1..+.COS.vcf-luigi-tmp', _args[1])
    assert _args[2].endswith('/CosmicGenomeScreensMutantExport.tsv')


def test_add_COSMIC_INFO(task, tmpdir):
    vcf = pytest.helpers.file('with_COSMIC_ids.vcf')
    new_vcf = tmpdir.join('with_COSMIC_INFO.vcf')
    cosmic_data_file = pytest.helpers.file('CosmicGenomeMutant.tsv')

    task.add_COSMIC_INFO(vcf, new_vcf, cosmic_data_file)

    with open(new_vcf) as f:
        lines = f.readlines()

    assert lines[2].startswith('##INFO=<ID=COSMIC')
    assert lines[3].startswith('#CHROM')

    assert 'FOO=BAR;COSMIC=GENE1|1|COSM0001|Confirmed_somatic_variant' in lines[4]
    assert '.;COSMIC=GENE1|1|COSM0001|Confirmed_somatic_variant,GENE2|2|COSM0002|Confirmed_somatic_variant' in lines[10]


def test_matches_to_INFO(task):
    rows = pd.DataFrame({
        'Gene name': ['GENE1', 'GENE2'],
        'Mutation ID': ['COSM1', 'COSM2'],
        'Mutation somatic status': ['Confirmed somatic', 'Previously observed']
    })
    result = task.matches_to_INFO(rows)
    assert result[0] == '##INFO=<ID=COSMIC,Number=1,Type=String,Description="Gene name|Mutation ID|Mutation somatic status">'
    assert result[1] == ';COSMIC=GENE1|COSM1|Confirmed_somatic,GENE2|COSM2|Previously_observed'


def test_read_COSMIC_mutation_info(task):
    path = pytest.helpers.file('CosmicGenomeMutant.tsv')
    result = task.read_COSMIC_mutation_info(path=path)
    assert len(result) == 2
    assert result.loc[0]['Gene name'] == 'GENE1'
    assert result.loc[1]['Gene name'] == 'GENE2'
    assert result.loc[0]['Mutation ID'] == 'COSM0001'
    assert result.loc[1]['Mutation ID'] == 'COSM0002'
