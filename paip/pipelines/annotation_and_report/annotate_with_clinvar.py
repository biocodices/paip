from anotamela.recipes import annotate_vcf_rsids_with_clinvar

from paip.task_types import CohortAnnotationTask
from paip.pipelines.variant_calling import FilterGenotypes


class AnnotateWithClinvar(CohortAnnotationTask):
    """
    Takes a VCF and generates a .json file with ClinVar annotations for all the
    rs IDs found.
    """
    REQUIRES = FilterGenotypes
    OUTPUT = 'clinvar_variants.json'

    def run(self):
        annotate_vcf_rsids_with_clinvar(
            vcf_path=self.input().fn,
            output_json_path=self.output().fn,
            **self.annotation_kwargs
        )
