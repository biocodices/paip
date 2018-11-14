from anotamela.recipes import annotate_vcf_rsids_with_dbsnp_web

from paip.task_types import CohortAnnotationTask
from paip.pipelines.variant_calling import FilterGenotypes


class AnnotateWithDbsnpWeb(CohortAnnotationTask):
    """
    Takes a VCF and generates a .json file with dbSNP Web annotations for all
    the rs IDs found.
    """
    REQUIRES = FilterGenotypes
    OUTPUT = 'dbsnp_annotations.json'

    def run(self):
        annotate_vcf_rsids_with_dbsnp_web(
            vcf_path=self.input().path,
            output_json_path=self.output().path,
            **self.annotation_kwargs
        )
