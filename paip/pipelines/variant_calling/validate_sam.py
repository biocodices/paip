import luigi

from paip.task_types import SampleTask
from paip.pipelines.variant_calling import FixReadGroups
from paip.helpers.create_cohort_task import create_cohort_task


class ValidateSam(SampleTask):
    """
    Takes a SAM and checks its valid. If it is, creates an empty file with the
    same name as the input SAM plus '.is_valid'.
    """
    REQUIRES = FixReadGroups
    OUTPUT_RENAMING = ('.sam', '.sam.validation_result')

    def output(self):
        path = self.input().path.replace('.sam', '.sam.validation_result')
        return luigi.LocalTarget(path)

    def run(self):
        input_sam = self.input().path
        validation_file = self.output().path

        with self.output()
        program_name = 'picard ValidateSamFile'
        program_options = {
            'input_sam': input_sam,
            'output_txt': validation_file,
        }
        self.run_program(program_name, program_options)

        with open(validation_file) as f:
             validation_file_contents = f.read()

        sam_is_valid = 'No errors found' in validation_file_contents
        if not sam_is_valid:
            raise InvalidSamException('SAM file appears not to be valid. '
                                      'Maybe the read groups fix went wrong? '
                                      f'Check: {input_sam}')


class InvalidSamException(Exception): pass


ValidateSamCohort = create_cohort_task(ValidateSam)
