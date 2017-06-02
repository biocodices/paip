import json
import luigi
from anotamela import AnnotationPipeline

from paip.task_types import CohortTask
from paip.pipelines.variant_calling import FilterGenotypes


class AnnotateVariants(CohortTask):
    """
    Annotates each sample's variants (taken from the reportable-variants VCF)
    and generates some JSON files with the annotations.

    This task will work if `anotamela` Python package is installed in the
    sytstem.
    """
    cache = luigi.Parameter(default='mysql')  # also: 'postgres', 'redis'
    http_proxy = luigi.Parameter(default='socks5://localhost:9050')

    # Receive an arbitrary JSON string with arguments for AnnotationPipeline.
    # They can be either annotation or cache keyword arguments.
    # If some argument is frequently used, you can extract it as a separate
    # parameter, as I already did with 'cache' and 'http_proxy' above.
    annotation_kwargs = luigi.Parameter(default='{}')

    OUTPUT = {
        'variants_json': 'rs_variants.json',
        'genes_json': 'genes.json',
    }

    def requires(self):
        # Remove the extra parameters that the annotation needs, but that
        # are not needed nor expected by the tasks upstream:
        params = self.param_kwargs.copy()

        del(params['cache'])
        del(params['http_proxy'])
        del(params['annotation_kwargs'])

        return FilterGenotypes(**params)

    def run(self):
        extra_kwargs = json.loads(self.annotation_kwargs)

        annotator = AnnotationPipeline(
            cache=self.cache,
            proxies={'http': self.http_proxy},
            **extra_kwargs
        )
        annotator.run_from_vcf(self.input().fn)

        rs_variants_json = annotator.rs_variants.to_json(orient='split')
        with open(self.output()['variants_json'].fn, 'w') as f:
            f.write(rs_variants_json)

        genes_json = annotator.gene_annotations.to_json(orient='split')
        with open(self.output()['genes_json'].fn, 'w') as f:
            f.write(genes_json)

