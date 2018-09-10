from os.path import join
import json

import luigi
from reports_generation import ReportsPipeline

from paip.task_types import SampleTask, CohortTask, ReportsTask
from paip.pipelines.annotation_and_report import (
    AnnotateWithSnpeff,
    AnnotateWithVEP,
    AnnotateVariants,
    AnnotateGenes,
)


class GenerateReports(ReportsTask, SampleTask):
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
        return {
            'vep': AnnotateWithVEP(**self.cohort_params()),
            'annotate_variants': AnnotateVariants(**self.cohort_params()),
            'annotate_genes': AnnotateGenes(**self.cohort_params()),
            'snpeff': AnnotateWithSnpeff(**self.sample_params()),
        }

    def run(self):
        """
        Generate HTML and CSV reports for a sample given its genotypes and
        the annotations for the variants and genes.
        """
        if self.phenos_regex_list:
            self.phenos_regex_list = json.loads(self.phenos_regex_list)

        reports_pipeline = ReportsPipeline(
            vep_tsv=self.input()['vep'].fn,
            genotypes_vcf=self.input()['snpeff'].fn,
            variants_json=self.input()['annotate_variants']['variants_json'].fn,
            genes_json=self.input()['annotate_genes'].fn,

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
        fn = f'{self.sample}.report_data_threshold_{self.min_reportable_category}.json'
        return {
            'report_json': luigi.LocalTarget(join(self.dir, fn)),
        }


class GenerateReportsCohort(CohortTask, ReportsTask, luigi.WrapperTask):
    SAMPLE_REQUIRES = GenerateReports
