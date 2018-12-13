from paip.helpers import generate_command, Config


def test_generate_command(config_test_files):
    options = {
        'foo_option': 'foo_value',
        'bar_option': 'bar_value',
    }
    config = Config()
    command = generate_command('program-2', options, config)
    expected_command = ('executable-2 --foo foo_value --bar bar_value '
                        '--resource /path/to/resource-1.txt')
    assert command == expected_command

    command = generate_command('command without executable', {}, config)
    assert command == 'some command without executable to fill in'
