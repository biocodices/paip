"""
This task will work if anotamela Python package is installed in the sytstem.
"""

import json
import luigi
from anotamela import AnnotationPipeline

from paip.task_types import SampleTask
from paip.pipelines.variant_calling import KeepReportableGenotypes


class AnnotateVariants(SampleTask):
    """
    Annotates each sample's variants (taken from the reportable-variants VCF)
    and generates some JSON files with the annotations.
    """
    cache = luigi.Parameter(default='mysql')  # also: 'postgres', 'redis'
    http_proxy = luigi.Parameter(default='socks5://localhost:9050')

    # Receive an arbitrary JSON string with arguments for AnnotationPipeline.
    # They can be either annotation or cache keyword arguments.
    # If some argument is frequently used, you can extract it as a separate
    # parameter, as we already did with 'cache' and 'http_proxy' above.
    extra_kwargs = luigi.Parameter(default='{}')

    REQUIRES = KeepReportableGenotypes
    OUTPUT = ['annotated_rs_variants.json',
              'annotated_genes.json']

    def run(self):
        extra_kwargs = json.loads(self.extra_kwargs)

        pipe = AnnotationPipeline(
            cache=self.cache,
            proxies={'http': self.http_proxy},
            **extra_kwargs
        )

        pipe.run_from_vcf(self.input().fn)

        with open(self.output()[0].fn, 'w') as f:
            f.write(pipe.rs_variants.to_json(orient='split'))

        with open(self.output()[1].fn, 'w') as f:
            f.write(pipe.gene_annotations.to_json(orient='split'))



