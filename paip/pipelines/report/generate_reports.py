from os.path import join
import json

import luigi
from reports_generation import ReportsPipeline

from paip.task_types import SampleTask, CohortTask, ReportsTask
from paip.pipelines.annotation import AnnotateVariants
from paip.pipelines.annotation import AnnotateGenes
from paip.pipelines.report import ExtractSample


class GenerateReports(ReportsTask, SampleTask):
    """
    Makes an HTML and a CSV report of the sample reportable variants.

    Report settings:

        - *min_odds_ratio*, the minimum odds ratio of a GWAS association
          to make a genotype reportable
        - *min_reportable_category*, the minimum pathogenicity category
          of an allele to be included in the reports
        - *max_frequency*, the maximum frequency (global MAF) for an allele
          to be reportable
        - *phenos_regex_list*, a JSON string with a list of phenotype patterns
          to keep in the report (non-matching phenotypes will not be included,
          no matter how serious their pathogenicity!)
        - *phenos_regex_file*, a plain text file with one regex per line
          of the phenotype patterns that should be kept

    This task uses the `reports_generation` Python package.
    """
    def requires(self):
        return {
            # ReportsTask.sample_params and .cohort_params remove the extra
            # parameters not needed by the tasks upstream:
            'sample_genotypes': ExtractSample(**self.sample_params()),
            'variant_annotations': AnnotateVariants(**self.cohort_params()),
            'gene_annotations': AnnotateGenes(**self.cohort_params()),
        }

    def run(self):
        """
        Generate HTML and CSV reports for a sample given its genotypes and
        the annotations for the variants and genes.
        """
        if self.phenos_regex_list:
            self.phenos_regex_list = json.loads(self.phenos_regex_list)

        with self.output().temporary_path() as temp_json:
            reports_pipeline = ReportsPipeline(
                genotypes_vcf=self.input()['sample_genotypes'].path,
                variants_json=\
                    self.input()['variant_annotations']['variants_json'].path,
                genes_json=self.input()['gene_annotations'].path,
                outdir=self.dir,
                out_report_path=temp_json,
                min_reportable_category=self.min_reportable_category,
                min_odds_ratio=self.min_odds_ratio,
                max_frequency=self.max_frequency,
                phenos_regex_list=self.phenos_regex_list,
                phenos_regex_file=self.phenos_regex_file,
            )
            reports_pipeline.run(samples=self.sample)

    def output(self):
        fn = (f'{self.sample}.report_data.' +
              f'min-cat-{self.min_reportable_category}.' +
              f'max-freq-{self.max_frequency}' +
              '.json')
        fp = join(self.dir, fn)
        return luigi.LocalTarget(fp)


class GenerateReportsCohort(CohortTask, ReportsTask, luigi.WrapperTask):
    SAMPLE_REQUIRES = GenerateReports
