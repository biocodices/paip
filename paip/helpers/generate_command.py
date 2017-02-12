from paip.helpers import Config


def generate_command(program_name, options):
    """
    Given a *program_name* and a dict of *options*, look for the
    command template of that program and populate the template holes
    with the values set for each option.

    The commands are looked by the Config class in ~/.paip/commands.yml
    """
    command_template = Config.commands(program_name)
    options.update({
        'executable': Config.executables(program_name)
    })
    return command_template.format(**options)

