from project.parsing.parsers.csv_parser import parse_csv
from project.parsing.parsers.json_parser import parse_json
from project.parsing.parsers.xml_parser import parse_xml
from project.parsing.parsers.txt_parser import parse_txt
from project.parsing.normalizer import normalize_entry
from project.parsing.categorizer import resolve_category
from project.parsing.inserter import insert_log_entries


print("DISPATCHER MODULE LOADED")

PARSERS = {
    "CSV": parse_csv,
    "JSON": parse_json,
    "XML": parse_xml,
    "TXT": parse_txt,
}

def process_file(db, file_obj, format_name, file_id):
    parser = PARSERS.get(format_name)
    if not parser:
        raise ValueError("Unsupported format")

    clean_entries = []

    for raw in parser(file_obj):
        entry = normalize_entry(raw)
        if not entry:
            continue

        entry["category"] = resolve_category(entry["message"])
        clean_entries.append(entry)

    print("FINAL CLEAN ENTRIES:", len(clean_entries))  # MUST be > 0

    insert_log_entries(db, file_id, clean_entries)
