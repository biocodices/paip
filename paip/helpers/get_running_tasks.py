from luigi.tools.luigi_grep import LuigiGrep


def get_running_tasks(host='localhost', port='8082'):
    """
    Get the current running tasks from Luigi's server. Optionally pass *host*
    and *port* of the Luigi server.

    Returns a list of strings.
    """
    luigi_grep = LuigiGrep(host=host, port=port)
    running_tasks = luigi_grep.status_search('RUNNING')

    return [task['name'].split('__')[0] for task in running_tasks]

