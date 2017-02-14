from paip.helpers import generate_command


def test_generate_command():
    options = {
        'foo_option': 'foo_value',
        'bar_option': 'bar_value',
    }
    command = generate_command('program-2', options)

    assert command == ('program-2-executable '
                       '--foo foo_value '
                       '--bar bar_value')

