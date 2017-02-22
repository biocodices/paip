from paip.helpers import Config, available_resources


def generate_command(program_name, options):
    """
    Given a *program_name* and a dict of *options*, look for the
    command template of that program and populate the template holes
    with the values set for each option.

    The commands are looked by the Config class in ~/.paip/commands.yml, and
    the options will be completed with:

      - all the resources found in ~/.paip/resources.yml,
        in case the commands use any of them
      - the path to the executable for the passed *program_name*,
        taken from ~/.paip/executables.yml.

    """
    # Use the first word of *program_name* to get the executable.
    # The reason is that "gatk SelectVariants", "gatk PrintReads", etc.,
    # should all use the same "gatk" executable. This also applies to
    # the subcommands of picard, for instance.
    executable = Config.executables(program_name.split(' ')[0])

    command_template = Config.commands(program_name)
    command_options = available_resources()
    command_options.update({
        'executable': executable
    })
    command_options.update(options)
    return command_template.format(**command_options)

