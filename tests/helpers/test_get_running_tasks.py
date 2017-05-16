from unittest.mock import MagicMock
from paip.helpers import get_running_tasks
from luigi.tools.luigi_grep import LuigiGrep


def test_get_running_tasks(monkeypatch):
    current_tasks = [
        {'name': 'Task1__foo__bar__baz__30__30__1234', 'status': 'RUNNING'},
        {'name': 'Task2__foo__bar__baz__30__30__1234', 'status': 'RUNNING'},
        {'name': 'Task3__foo__bar__baz__30__30__1234', 'status': 'RUNNING'},
    ]
    mock_status_search = MagicMock(return_value=current_tasks)
    monkeypatch.setattr(LuigiGrep, 'status_search', mock_status_search)
    running_tasks = get_running_tasks()
    assert running_tasks == ['Task1', 'Task2', 'Task3']

