"""
This is a json parser
"""

import json

def parse_json(file_obj):
    """
    Docstring for parse_json
    this is parser will convert into json object to string dictionary type
    
    :param file_obj: input file
    """
    data = json.loads(file_obj.read().decode("utf-8"))
    for item in data:
        yield item
