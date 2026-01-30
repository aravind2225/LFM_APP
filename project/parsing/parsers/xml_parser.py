import xml.etree.ElementTree as ET

def parse_xml(file_obj):
    tree = ET.fromstring(file_obj.read().decode("utf-8"))
    for log in tree.findall("log"):
        yield {
            "timestamp": log.findtext("timestamp"),
            "severity": log.findtext("level"),
            "message": log.findtext("message")
        }
