import json


def save_value(key, value):
    with open('./db.json', 'r') as f:
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError:
            data = {}

    data[key] = value

    with open('./db.json', mode='w') as f:
        json.dump(data, f)


def load_value(key):
    with open('./db.json') as f:
        try:
            data = json.load(f)
            return data.get(key)
        except (json.decoder.JSONDecodeError, KeyError):
            return None
