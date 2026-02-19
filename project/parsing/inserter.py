"""
This is a function to insert the logs into db
"""

from sqlalchemy import text

def insert_log_entries(db, file_id, entries):
    """
    Docstring for insert_log_entries
    insert the logs one by one into DB
    
    :param db: DB Instance
    :param file_id: raw_file id
    :param entries: list of clean logs to be inserted
    """
    for e in entries:
        db.execute(
            text("""
                INSERT INTO log_entries (
                    file_id,
                    log_timestamp,
                    severity_id,
                    category_id,
                    message_line
                )
                VALUES (
                    :file_id,
                    :ts,
                    (SELECT severity_id FROM log_severities WHERE severity_code = :sev),
                    (SELECT category_id FROM log_categories WHERE category_name = :cat),
                    :msg
                )
                ON CONFLICT DO NOTHING
            """),
            {
                "file_id": file_id,
                "ts": e["timestamp"],
                "sev": e["severity"],
                "cat": e["category"],
                "msg": e["message"]
            }
        )
