from paip.task_types import CohortAnnotationTask
from paip.pipelines.variant_calling import AnnotateWithDbsnpWeb

from anotamela.annotators import GeneEntrezAnnotator


class AnnotateWithGeneEntrez(CohortAnnotationTask):
    """
    Takes a JSON file of DbSNP annotations and annotates the genes
    found there. The result is put in a new JSON file for gene annotations.
    """
    REQUIRES = AnnotateWithDbsnpWeb
    OUTPUT = 'gene_entrez_annotations.json'

    def run(self):
        #
        #
        # SEGUIR ACA:
        #

        # Extract the gene_entrez_ids from input().fn

        gene_entrez = GeneEntrezAnnotator(**self.annotation_kwargs)
        annotations = gene_entrez.annotate(gene_entrez_ids)

        # put annotations in the output().fn
