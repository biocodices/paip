from paip.helpers import generate_command


def test_generate_command(config_test_files):
    options = {
        'foo_option': 'foo_value',
        'bar_option': 'bar_value',
    }

    command = generate_command('program-2', options)
    expected_command = 'program-2-executable --foo foo_value --bar bar_value'
    assert command == expected_command

    command = generate_command('program-2 subcommand', options)
    assert command == expected_command

