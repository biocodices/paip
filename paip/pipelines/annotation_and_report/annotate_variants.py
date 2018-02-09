from anotamela import AnnotationPipeline

from paip.task_types import CohortAnnotationTask
from paip.pipelines.variant_calling import FilterGenotypes


class AnnotateVariants(CohortAnnotationTask):
    """
    Annotates each sample's variants (taken from the reportable-variants VCF)
    and generates some JSON files with the annotations.

    This task will work if `anotamela` Python package is installed in the
    sytstem.
    """
    REQUIRES = FilterGenotypes
    OUTPUT = {
        'variants_json': 'rs_variants.json',
        'genes_json': 'genes.json',
    }

    def run(self):
        annotator = AnnotationPipeline(**self.annotation_kwargs)
        annotator.run_from_vcf(self.input().fn)

        rs_variants_json = annotator.rs_variants.to_json(orient='split')
        with open(self.output()['variants_json'].fn, 'w') as f:
            f.write(rs_variants_json)

        genes_json = annotator.gene_annotations.to_json(orient='split')
        with open(self.output()['genes_json'].fn, 'w') as f:
            f.write(genes_json)

