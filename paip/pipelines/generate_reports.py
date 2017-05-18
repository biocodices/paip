from os.path import join

import luigi
from reports_generation import ReportsPipeline

from paip.task_types import SampleTask
from paip.pipelines.variant_calling import AnnotateWithSnpeff


# TODO:
# Create a GenerateReports Cohort Task that requires
# AnnotateWithVEP and AnnotateVariants
# and runs GenerateReports for each sample in the cohort

# It should share and pass down all the relevant params
# with/to the sample task


# TODO:
# Make this accept --phenos-regex-file or --phenos-regex-list
# parameters


class GenerateReports(SampleTask):
    """
    Makes an HTML and a CSV report of the sample reportable variants.

    Takes annotation files:

        - *vep_tsv* with Variant Effect Predictor annotations
        - *variants_json* with the result from `anotamela` (RSIDs)
        - *genes_json* with the result from `anotamela` (genes of the RSIDs)

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

    This task will work if `reports_generation` Python package is installed
    in the system.
    """
    # Files with annotations
    vep_tsv = luigi.Parameter()
    variants_json = luigi.Parameter()
    genes_json = luigi.Parameter()

    # Directories
    templates_dir = luigi.Parameter()
    translations_dir = luigi.Parameter()

    # Reportable variants settings
    min_odds_ratio = luigi.FloatParameter(default=1)  # All by default
    max_frequency = luigi.FloatParameter(default=1)  # All by default
    min_reportable_category = luigi.Parameter(default='DRUG')

    def requires(self):
        # Remove the extra parameters that the report generation needs, but
        # that are not needed nor expected by the tasks upstream:
        params = self.param_kwargs.copy()

        extra_params = [
            'vep_tsv',
            'variants_json',
            'genes_json',
            'templates_dir',
            'translations_dir',
            'min_odds_ratio',
            'max_frequency',
            'min_reportable_category',
        ]
        for param_name in extra_params:
            del(params[param_name])

        return AnnotateWithSnpeff(**params)

    def run(self):
        """
        Generate HTML and CSV reports for a sample given its genotypes and
        the annotations for the variants and genes.
        """
        reports_pipeline = ReportsPipeline(
            genotypes_vcf=self.input().fn,

            vep_tsv=self.vep_tsv,
            variants_json=self.variants_json,
            genes_json=self.genes_json,

            templates_dir=self.templates_dir,
            translations_dir=self.translations_dir,
            outdir=self.dir,

            min_reportable_category=self.min_reportable_category,
            min_odds_ratio=self.min_odds_ratio,
            max_frequency=self.max_frequency,
        )

        reports_pipeline.run(samples=self.sample)

    def output(self):
        fp = join(self.dir, 'report_{}'.format(self.sample), 'index.html')
        return luigi.LocalTarget(fp)

