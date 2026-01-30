import json

def parse_json(file_obj):
    data = json.loads(file_obj.read().decode("utf-8"))
    for item in data:
        yield item
