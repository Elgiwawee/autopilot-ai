# cloud/utils/json.py

import json


def json_safe(data):
    return json.loads(
        json.dumps(
            data,
            default=str
        )
    )