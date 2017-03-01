from paip.variant_calling import KeepReportableGenotypes
from paip.task_types import SampleTask


class BcftoolsStats(SampleTask):
    """
    Takes a VCF and creates a stats file of its variants using bcftools stats.
    """
    REQUIRES = KeepReportableGenotypes
    OUTPUT = 'bcftools_stats'

    def run(self):
        program_name = 'bcftools stats'
        program_options = {
            'input_vcf': self.input().fn,
        }

        stdout, _ = self.run_program(program_name, program_options,
                                     log_stdout=False)

        with open(self.output().fn, 'wb') as f:
            f.write(stdout)

