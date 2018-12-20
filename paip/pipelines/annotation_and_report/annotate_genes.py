import re
from inspect import signature

from anotamela.pipeline import annotate_entrez_gene_ids

from paip.task_types import CohortAnnotationTask
from paip.pipelines.annotation_and_report import AnnotateWithVEP
from paip.helpers import read_vep_tsv, prettify_JSON_dump


class AnnotateGenes(CohortAnnotationTask):
    """
    Annotates all Entrez gene IDs found in the VEP annotation .tsv file.
    Generates a JSON file with the annotations for each gene.
    """
    REQUIRES = AnnotateWithVEP
    OUTPUT = 'genes.json'

    def run(self):
        entrez_gene_ids = extract_entrez_gene_ids_from_vep_tsv(self.input().path)
        sig = signature(annotate_entrez_gene_ids)
        annotation_params = {k: v for k, v in self.annotation_kwargs.items()
                             if k in sig.parameters.keys()}
        gene_annotations = annotate_entrez_gene_ids(entrez_gene_ids,
                                                    **annotation_params)
        genes_json = gene_annotations.to_json(orient='split')
        genes_json = prettify_JSON_dump(genes_json)

        with open(self.output().path, 'w') as f:
            f.write(genes_json)


def extract_entrez_gene_ids_from_vep_tsv(tsv_path):
    """
    Extract a unique list of Entrez gene IDs from VEP's .tsv annotation
    file. Removes any Ensemble gene IDs found.
    """
    vep_annotations = read_vep_tsv(tsv_path)
    gene_ids = vep_annotations['gene'].dropna().unique()
    print([g for g in gene_ids if not isinstance(g, str)])
    return [gene_id for gene_id in gene_ids if re.search(r'^[0-9]+$', gene_id)]
