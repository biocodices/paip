def generate_command(program_name, options, config):
    """
    Given a *program_name* and a dict of *options*, look for the
    command template of that program and populate the template holes
    with the values set for each option.

    The executable paths, the command syntax, and the path to resources are
    fetched with the help of the *config* object passed.
    """
    # Use the first word of *program_name* to get the executable.
    # The reason is that "gatk SelectVariants", "gatk PrintReads", etc.,
    # should all use the same "gatk" executable. This also applies to
    # the subcommands of picard, samtools, etc.
    executable = config.executables[program_name.split(' ')[0]]
    command_template = config.commands[program_name]
    command_options = config.resources
    command_options.update({
        'executable': executable
    })
    command_options.update(options)
    return command_template.format(**command_options)
