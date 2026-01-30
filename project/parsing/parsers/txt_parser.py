import re

TIMESTAMP_REGEX = re.compile(
    r"^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(?:[.,]\d{3})?"
)

def parse_txt(file_obj):
    """
    Groups multiline log entries into single logical events.
    """
    buffer = []

    for raw in file_obj:
        line = raw.decode("utf-8", errors="ignore").rstrip()

        if not line:
            continue

        # New log entry starts
        if TIMESTAMP_REGEX.match(line):
            if buffer:
                yield "\n".join(buffer)
                buffer = []
            buffer.append(line)
        else:
            # Continuation (stack trace, wrapped line)
            buffer.append(line)

    if buffer:
        yield "\n".join(buffer)
