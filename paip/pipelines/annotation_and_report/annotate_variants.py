import json

from anotamela import AnnotationPipeline

from paip.task_types import CohortAnnotationTask
from paip.pipelines.variant_calling import FilterGenotypes


class AnnotateVariants(CohortAnnotationTask):
    """
    Annotates each sample's variants (taken from the reportable-variants VCF)
    and generates some JSON files with the annotations.

    This task will work if `anotamela` Python package is installed.
    """
    REQUIRES = FilterGenotypes
    OUTPUT = {
        'variants_json': 'rs_variants.json',
        'other_variants_json': 'other_variants.json',
        # 'genes_json': 'genes.json',
    }

    def run(self):
        annotator = AnnotationPipeline(**self.annotation_kwargs)
        annotator.run_from_vcf(self.input().path)

        rs_variants_json = annotator.rs_variants.to_json(orient='split')
        rs_variants_json = self.prettify_pandas_JSON_dump(rs_variants_json)

        with open(self.output()['variants_json'].path, 'w') as f:
            f.write(rs_variants_json)

        other_variants_json = annotator.other_variants.to_json(orient='split')
        other_variants_json = self.prettify_pandas_JSON_dump(other_variants_json)

        with open(self.output()['other_variants_json'].path, 'w') as f:
            f.write(other_variants_json)

        ## We now use a separate task to annotate the genes, not from the
        ## rs_ids annotations, but from VEP annotations!
        #  genes_json = annotator.gene_annotations.to_json(orient='split')
        #  with open(self.output()['genes_json'].path, 'w') as f:
            #  f.write(genes_json)

    def prettify_pandas_JSON_dump(self, json_from_pandas):
        """
        Pandas .to_json does not have an option to make the JSON dump look
        pretty, so it's written all in one line. This is a hack to solve that.
        """
        loaded_object = json.loads(json_from_pandas)
        prettified = json.dumps(loaded_object, indent=2)
        return prettified
