from sqlalchemy import text

def insert_log_entries(db, file_id, entries):
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
            """),
            {
                "file_id": file_id,
                "ts": e["timestamp"],
                "sev": e["severity"],
                "cat": e["category"],
                "msg": e["message"]
            }
        )
