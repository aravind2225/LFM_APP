"""
This is the central Query File for all SQL Queries
"""

QUERIES = {

    # ======================
    # DASHBOARD METRICS
    # ======================

    "TOTAL_ACTIVE_USERS": """
        SELECT COUNT(*)
        FROM users
        WHERE is_active = true
    """,

    "TOTAL_FILES": """
        SELECT COUNT(*)
        FROM raw_files
        WHERE is_archived = false
    """,

    "TOTAL_LOGS": """
        SELECT COUNT(*)
        FROM log_entries le
        JOIN raw_files rf ON le.file_id = rf.file_id
        WHERE rf.is_archived = false
    """,

    "TOTAL_ERRORS": """
        SELECT COUNT(*)
        FROM log_entries le
        JOIN raw_files rf ON le.file_id = rf.file_id
        WHERE rf.is_archived = false
          AND le.severity_id = 4
    """,

    "LAST_FILE_UPLOADED_AT": """
        SELECT COALESCE(
            MAX(uploaded_at)::timestamp,
            '2035-01-01 00:00:00+00'::timestamp
        )
        FROM raw_files
    """,

    "TOTAL_ARCHIVED_FILES": """
        SELECT COUNT(*)
        FROM raw_files
        WHERE is_archived = true
    """,

    "TOTAL_ACTIONS": """
        SELECT COUNT(*)
        FROM audit_trail
    """,

    "BIGGEST_FILE_NAME": """
        SELECT original_name
        FROM raw_files
        WHERE file_size_bytes = (
            SELECT MAX(file_size_bytes)
            FROM raw_files
            WHERE is_archived = false
        )
        LIMIT 1
    """,

    "AVG_LOGS_PER_FILE": """
        SELECT ROUND(
            COUNT(*)::decimal /
            NULLIF(COUNT(DISTINCT rf.file_id), 0),
            2
        )
        FROM log_entries le
        JOIN raw_files rf ON le.file_id = rf.file_id
        WHERE rf.is_archived = false
    """,

    "AVG_ERRORS_PER_FILE": """
        SELECT ROUND(
            COUNT(*)::decimal /
            NULLIF(COUNT(DISTINCT rf.file_id), 0),
            2
        )
        FROM log_entries le
        JOIN raw_files rf ON le.file_id = rf.file_id
        WHERE rf.is_archived = false
          AND le.severity_id = 4
    """,

    "TOP_CONTRIBUTOR_TEAM": """
        SELECT t.team_name
        FROM raw_files rf
        JOIN teams t ON t.team_id = rf.team_id
        GROUP BY t.team_name
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """,

    "TOP_CONTRIBUTOR_USER": """
        SELECT u.username
        FROM raw_files rf
        JOIN users u ON u.user_id = rf.uploaded_by
        GROUP BY u.username
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """,

    # ======================
    # CHART QUERIES
    # ======================

    "FILES_BY_TEAMS": """
        SELECT t.team_name,
               COUNT(*) AS total_uploads
        FROM raw_files rf
        JOIN teams t ON rf.team_id = t.team_id
        GROUP BY t.team_name
    """,

    "FILES_BY_DATES": """
        SELECT DATE(uploaded_at) AS date,
               COUNT(*) AS total_files
        FROM raw_files
        GROUP BY DATE(uploaded_at)
        ORDER BY DATE(uploaded_at)
    """,

    # ======================
    # SEVERITY ANALYSIS
    # ======================

    "LOG_SEVERITY_DISTRIBUTION": """
        SELECT ls.severity_code,
               COUNT(le.log_id) AS nlog
        FROM log_entries le
        JOIN log_severities ls
            ON le.severity_id = ls.severity_id
        GROUP BY ls.severity_code
        ORDER BY nlog DESC
    """,

    # ======================
    # USER ANALYTICS
    # ======================

    "MOST_ACTIVE_USERS_LAST_7_DAYS": """
        SELECT u.username,
               COUNT(rf.file_id) AS fcount
        FROM raw_files rf
        JOIN users u ON rf.uploaded_by = u.user_id
        WHERE uploaded_at > NOW() - INTERVAL '7 days'
        GROUP BY u.username
        HAVING COUNT(rf.file_id) > 3
    """,

    # ======================
    # SECURITY LOGS
    # ======================

    "SECURITY_LOGS_LAST_WEEK": """
        SELECT
            le.log_id,
            rf.original_name,
            le.log_timestamp::timestamp(0) AS ts,
            ls.severity_code,
            le.message_line
        FROM log_entries le
        JOIN raw_files rf ON le.file_id = rf.file_id
        JOIN log_severities ls ON le.severity_id = ls.severity_id
        WHERE category_id = 2
          AND created_at > NOW() - INTERVAL '7 days'
    """,



    # ======================
    # USER-SCOPED METRICS
    # ======================

    "FILES_SELF": """
        SELECT COUNT(*)
        FROM raw_files
        WHERE uploaded_by = :uid
          AND is_archived = false
    """,

    "LOGS_SELF": """
        SELECT COUNT(*)
        FROM log_entries le
        JOIN raw_files rf ON le.file_id = rf.file_id
        WHERE rf.uploaded_by = :uid
          AND rf.is_archived = false
    """,

    "ERRORS_SELF": """
        SELECT COUNT(*)
        FROM log_entries le
        JOIN raw_files rf ON le.file_id = rf.file_id
        WHERE rf.uploaded_by = :uid
          AND rf.is_archived = false
          AND le.severity_id = 4
    """,

    "LAST_UPLOADED_SELF": """
        SELECT COALESCE(
            MAX(uploaded_at),
            '2035-01-01 00:00:00+00'::timestamptz
        )
        FROM raw_files
        WHERE uploaded_by = :uid
    """,

    "USER_LATEST_TEAM_ID": """
        SELECT team_id
        FROM user_teams
        WHERE user_id = :uid
        ORDER BY joined_at DESC
        LIMIT 1
    """,

    # ======================
    # TEAM-SCOPED METRICS
    # ======================

    "FILES_TEAM": """
        SELECT COUNT(*)
        FROM raw_files
        WHERE team_id = :tid
          AND is_archived = false
    """,

    "LOGS_TEAM": """
        SELECT COUNT(*)
        FROM log_entries le
        JOIN raw_files rf ON le.file_id = rf.file_id
        WHERE rf.team_id = :tid
          AND rf.is_archived = false
    """,

    "ERRORS_TEAM": """
        SELECT COUNT(*)
        FROM log_entries le
        JOIN raw_files rf ON le.file_id = rf.file_id
        WHERE rf.team_id = :tid
          AND rf.is_archived = false
          AND le.severity_id = 4
    """,

    "ARCHIVES_TEAM": """
        SELECT COUNT(*)
        FROM raw_files
        WHERE team_id = :tid
          AND is_archived = true
    """


}
