from os.path import join, dirname

from paip.helpers import Config, Resource
from paip.programs import ProgramCaller
from paip.helpers.general import params_dict_to_str


def trim_adapters(forward_reads, reverse_reads):
    """
    Expects two filepaths: forward and reverse .fastq files of the same
    sample. It will search for an adapters file defined in resources.yml.
    """
    fastqs = [forward_reads, reverse_reads]
    trimmed_fastqs = [filepath.replace('.fastq', '.trimmed.fastq')
                      for filepath in fastqs]

    params_dict = Config.parameters()['fastq-mcf']
    executable_path = Config.executables['fastq-mcf']

    params_str = params_dict_to_str(params_dict)
    for trimmed_fastq in trimmed_fastqs:
        params_str += ' -o {}'.format(trimmed_fastq)

    command = '{} {}'.format(executable_path, params_str)
    adapters_file = Resource('illumina_adapters_file')
    command += ' {} {} {}'.format(adapters_file, *reads_filepaths)

    log_filepath = join(dirname(trimmed_fastqs[0]), 'fastq-mcf')
    return command
    #  ProgramCaller(command).run(log_filepath=log_filepath)

    #  return trimmed_fastqs

