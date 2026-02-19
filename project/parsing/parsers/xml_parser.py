"""
This is an XML parser
"""

import xml.etree.ElementTree as ET

def parse_xml(file_obj):
    """
    Docstring for parse_xml
    This will convert the XML Objects into dictionary object
    
    :param file_obj: input file
    """
    tree = ET.fromstring(file_obj.read().decode("utf-8"))
    for log in tree.findall("log"):
        yield {
            "timestamp": log.findtext("timestamp"),
            "severity": log.findtext("level") or log.findtext("severity"),
            "message": log.findtext("message") or log.findtext('content')
        }
