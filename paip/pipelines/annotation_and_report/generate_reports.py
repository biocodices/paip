from os.path import join
import json

import luigi
from reports_generation import ReportsPipeline

from paip.task_types import SampleTask, CohortTask
from paip.pipelines.annotation_and_report import (
    AnnotateWithSnpeff,
    AnnotateWithVEP,
    AnnotateVariants,
)


class ReportsTask:
    """
    Abstract class to provide common parameters to GenerateReports and
    GenerateReportsCohort. See the former class for a full explanation of
    each parameter.
    """
    # Directories
    templates_dir = luigi.Parameter()
    translations_dir = luigi.Parameter()

    # Reportable variants settings
    min_odds_ratio = luigi.FloatParameter(default=1)  # All by default
    max_frequency = luigi.FloatParameter(default=1)  # All by default
    min_reportable_category = luigi.Parameter(default='DRUG')
    phenos_regex_list = luigi.Parameter(default=None)
    phenos_regex_file = luigi.Parameter(default=None)


class GenerateReports(SampleTask, ReportsTask):
    """
    Makes an HTML and a CSV report of the sample reportable variants.

    Report templates:

        - *templates_dir* with at least a `base.html.jinja` template
          for the HTML report generation
        - *translations_dir* with a directory of translation texts to be
          used in the template

    And report settings:

        - *min_odds_ratio*, the minimum odds ratio of a GWAS association
          to make a genotype reportable
        - *max_frequency*, the maximum frequency (global MAF) for an allele
          to be reportable
        - *min_reportable_category*, the minimum pathogenicity category
          of an allele to be included in the reports
        - *phenos_regex_list*, a JSON string with a list of phenotype patterns
          to keep in the report (non-matching phenotypes will not be included,
          no matter how serious their pathogenicity!)
        - *phenos_regex_file*, a plain text file with one regex per line
          of the phenotype patterns that should be kept

    This task will work if `reports_generation` Python package is installed
    in the system.
    """
    def requires(self):
        # Remove the extra parameters that the report generation needs, but
        # that are not needed nor expected by the tasks upstream:
        sample_params = self.param_kwargs.copy()

        extra_params = [
            'templates_dir',
            'translations_dir',
            'min_odds_ratio',
            'max_frequency',
            'min_reportable_category',
            'phenos_regex_list',
            'phenos_regex_file',
        ]
        for param_name in extra_params:
            del(sample_params[param_name])

        cohort_params = sample_params.copy()
        del(cohort_params['sample'])

        return [
            AnnotateWithVEP(**cohort_params),  # vep.tsv
            AnnotateVariants(**cohort_params),  # rs_variants.json, genes.json
            AnnotateWithSnpeff(**sample_params),  # .eff.vcf
        ]

    def run(self):
        """
        Generate HTML and CSV reports for a sample given its genotypes and
        the annotations for the variants and genes.
        """
        if self.phenos_regex_list:
            self.phenos_regex_list = json.loads(self.phenos_regex_list)

        reports_pipeline = ReportsPipeline(
            vep_tsv=self.input()[0].fn,  # AnnotateWithVEP
            variants_json=self.input()[1][0].fn,  # AnnotateVariants
            genes_json=self.input()[1][1].fn,  # AnnotateVariants
            genotypes_vcf=self.input()[2].fn,  # AnnotateWithSnpeff

            templates_dir=self.templates_dir,
            translations_dir=self.translations_dir,
            outdir=self.dir,

            min_reportable_category=self.min_reportable_category,
            min_odds_ratio=self.min_odds_ratio,
            max_frequency=self.max_frequency,
            phenos_regex_list=self.phenos_regex_list,
            phenos_regex_file=self.phenos_regex_file,
        )

        reports_pipeline.run(samples=self.sample)

    def output(self):
        fp = join(self.dir, 'report_{}'.format(self.sample), 'index.html')
        return luigi.LocalTarget(fp)


class GenerateReportsCohort(CohortTask, ReportsTask, luigi.WrapperTask):
    SAMPLE_REQUIRES = GenerateReports

