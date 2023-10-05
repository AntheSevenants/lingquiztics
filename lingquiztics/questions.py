import json

def load(path):
    with open(path, "rt") as reader:
        content = reader.read()

    return json.loads(content)