from paip.task_types import CohortTask
from paip.variant_calling import AnnotateWithSnpeff
from paip.quality_control import FastQC, AlignmentMetrics


class MultiQC(CohortTask):
    """
    Expects several quality control programs to have run. Summarizes all those
    results in a single HTML report for the cohort.
    """
    def requires(self):
        ##
        ## FIXME: I should include a Snpeff stats generation for the *sample*
        ##        on the reportable.vcf file, to make sure all samples
        ##        end up with the same amount of reportable genotypes (panel)
        ##
        tasks = [AnnotateWithSnpeff(**self.param_kwargs)]

        for sample in self.sample_list:
            tasks.append(FastQC(sample=sample, basedir=self.basedir))
            tasks.append(AlignmentMetrics(sample=sample, basedir=self.basedir))

        return tasks

    OUTPUT = ['R1_fastqc.html', 'R1.trimmed_fastqc.html',
              'R2_fastqc.html', 'R2.trimmed_fastqc.html']

    def run(self):
        program_name = 'fastqc'

        # Run on raw reads (CheckFastqs output)
        raw_fastqs = self.input()[0]
        program_options = {
            'forward_reads': raw_fastqs[0].fn,
            'reverse_reads': raw_fastqs[1].fn,
        }
        self.run_program(program_name, program_options)

        # Run on trimmed reads (TrimAdapters output)
        trimmed_fastqs = self.input()[1]
        program_options = {
            'forward_reads': trimmed_fastqs[0].fn,
            'reverse_reads': trimmed_fastqs[1].fn,
        }
        self.run_program(program_name, program_options)

