import json

from paip.task_types import CohortAnnotationTask
from paip.pipelines.annotation import AnnotateWithDbsnpWeb

from anotamela.annotators import GeneEntrezAnnotator


class AnnotateWithGeneEntrez(CohortAnnotationTask):
    """
    Takes a JSON file of DbSNP annotations and annotates the genes
    found there. The result is put in a new JSON file for gene annotations.
    """
    REQUIRES = AnnotateWithDbsnpWeb
    OUTPUT = 'gene_entrez_annotations.json'

    def run(self):
        # Extract the gene_entrez_ids from the input file
        gene_entrez_ids = \
            self._extract_gene_entrez_ids_from_dbsnp_annotations(self.input().path)

        # Annotate those gene ids
        gene_entrez = GeneEntrezAnnotator(**self.annotation_kwargs)
        gene_annotations = list(gene_entrez.annotate(gene_entrez_ids).values())

        # Write the annotations to the output file
        with open(self.output().path, 'w') as f:
            json.dump(gene_annotations, f)

    @staticmethod
    def _extract_gene_entrez_ids_from_dbsnp_annotations(dbsnp_annotations_json):
        """
        Take a JSON file of dbsnp annotations, each of which are expected to have
        entries of gene_entrez_ids. Extract those IDs into a unique list.
        """
        with open(dbsnp_annotations_json) as f:
            dbsnp_annotations = json.load(f)

        gene_entrez_ids = []
        for dbsnp_annotation in dbsnp_annotations:
            gene_entrez_ids += dbsnp_annotation.get('GRCh37.p13_gene_entrez_ids', [])
            gene_entrez_ids += dbsnp_annotation.get('GRCh38.p7_gene_entrez_ids', [])

        return sorted(set(gene_entrez_ids))
