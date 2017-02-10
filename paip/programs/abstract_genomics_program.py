from paip.helpers import Config, path_to_resource


class AbstractGenomicsProgram:
    def __init__(self, program_name):
        self.executable = Config.executables(program_name)
        self.params = Config.parameters(program_name)
        self.reference_genome = path_to_resource('reference_genome')
        self.reference_genome_dict = path_to_resource('reference_genome_dict')
        self.known_indels = [path_to_resource('indels_1000G'),
                             path_to_resource('indels_mills')]
        self.panel_amplicons = path_to_resource('panel_amplicons')
        self.known_variants = path_to_resource('dbsnp_GRCh37')
        self.panel_design_vcf = path_to_resource('panel_design_vcf')
