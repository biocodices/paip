import json


def prettify_JSON_dump(json_dump):
    """
    Pandas .to_json does not have an option to make the JSON dump look
    pretty, so it's written all in one line. This is a hack to solve that.
    """
    loaded_object = json.loads(json_dump)
    prettified = json.dumps(loaded_object, indent=2)
    return prettified
