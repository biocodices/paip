import subprocess
from unittest.mock import Mock

from paip.helpers import X_server


def test_X_server(monkeypatch):
    mock_process = Mock(name='spawned_process')
    mock_Popen = Mock(name='Popen', return_value=(mock_process))
    monkeypatch.setattr(subprocess, 'Popen', mock_Popen)

    with X_server(77) as port_number:
        assert port_number == 77
        assert mock_Popen.called_once_with(['Xvfb', ':77'])
        assert mock_process.kill.call_count == 0

    mock_process.kill.assert_called_once_with()

