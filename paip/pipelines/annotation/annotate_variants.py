from anotala import AnnotationPipeline

from paip.task_types import CohortAnnotationTask
from paip.pipelines.annotation import AnnotateDbsnpId
from paip.helpers import prettify_JSON_dump


class AnnotateVariants(CohortAnnotationTask):
    """
    Annotates each sample's variants (taken from the reportable-variants VCF)
    and generates some JSON files with the annotations.

    This task will work if `anotala` Python package is installed.
    """
    REQUIRES = AnnotateDbsnpId
    OUTPUT = {
        'variants_json': 'rs_variants.json',
        'other_variants_json': 'other_variants.json',
    }

    def run(self):
        ann_pipe = AnnotationPipeline(**self.annotation_kwargs)
        ann_pipe.run_from_vcf(self.input().path)

        rs_variants_json = ann_pipe.rs_variants.to_json(orient='split')
        rs_variants_json = prettify_JSON_dump(rs_variants_json)

        with open(self.output()['variants_json'].path, 'w') as f:
            f.write(rs_variants_json)

        other_variants_json = ann_pipe.other_variants.to_json(orient='split')
        other_variants_json = prettify_JSON_dump(other_variants_json)

        with open(self.output()['other_variants_json'].path, 'w') as f:
            f.write(other_variants_json)
