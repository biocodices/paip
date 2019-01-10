from inspect import signature

from anotamela.annotators import GeneEntrezLocalAnnotator
from anotamela.pipeline import annotate_entrez_gene_ids

from paip.task_types import CohortAnnotationTask
from paip.pipelines.annotation import AnnotateWithSnpeff
from paip.helpers import prettify_JSON_dump


class AnnotateGenes(CohortAnnotationTask):
    """
    Annotates all Entrez gene IDs found in the VEP annotation .tsv file.
    Generates a JSON file with the annotations for each gene.
    """
    REQUIRES = AnnotateWithSnpeff
    OUTPUT = 'genes.json'

    def read_gene_symbols(self, path):
        """
        Extract a unique list of Entrez gene symbols from the *path*.
        """
        with open(path) as f:
            return [line.split()[0] for line in f if not line.startswith('#')]

    def gene_symbols_to_entrez_ids(self, gene_symbols):
        annotator = GeneEntrezLocalAnnotator()
        annotations = annotator.annotate(gene_symbols)
        return sorted(set(ann['GeneID'] for ann in annotations.values()))

    def run(self):
        snpeff_annotation = self.requires()
        gene_symbols = self.read_gene_symbols(snpeff_annotation.genes_txt)
        entrez_gene_ids = self.gene_symbols_to_entrez_ids(gene_symbols)

        # Annotate the entrez gene Ids
        sig = signature(annotate_entrez_gene_ids)
        annotation_params = {k: v for k, v in self.annotation_kwargs.items()
                             if k in sig.parameters.keys()}
        gene_annotations = annotate_entrez_gene_ids(entrez_gene_ids,
                                                    **annotation_params)
        genes_json = gene_annotations.to_json(orient='split')
        genes_json = prettify_JSON_dump(genes_json)

        with open(self.output().path, 'w') as f:
            f.write(genes_json)
