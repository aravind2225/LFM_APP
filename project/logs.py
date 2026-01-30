from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import text

from project.db import get_db

logs_bp = Blueprint("logs", __name__, url_prefix="/logs")


@logs_bp.route("/view", methods=["GET"])
@login_required
def view_logs():
    db = get_db()

    # ---- Filters from query params ----
    ownership = request.args.get("ownership", "me")  # me | team
    severity = request.args.get("severity")
    category = request.args.get("category")
    environment = request.args.get("environment")

    # ---- Resolve team_id ----
    team_id = db.execute(
        text("""
            SELECT team_id FROM user_teams
            WHERE user_id = :uid order by joined_at desc limit 1
        """),
        {"uid": current_user.id}
    ).scalar()

    params = {"team_id": team_id}
    conditions = ["rf.team_id = :team_id"]

    if ownership == "me":
        conditions.append("rf.uploaded_by = :uid")
        params["uid"] = current_user.id

    if severity:
        conditions.append("s.severity_code = :severity")
        params["severity"] = severity

    if category:
        conditions.append("c.category_name = :category")
        params["category"] = category

    if environment:
        conditions.append("e.environment_code = :env")
        params["env"] = environment

    query = f"""
        SELECT
            le.log_timestamp,
            s.severity_code,
            c.category_name,
            e.environment_code,
            le.message_line,
            u.username AS uploaded_by,
            rf.original_name
        FROM log_entries le
        JOIN raw_files rf     ON rf.file_id = le.file_id
        JOIN users u          ON u.user_id = rf.uploaded_by
        JOIN log_severities s ON s.severity_id = le.severity_id
        JOIN log_categories c ON c.category_id = le.category_id
        JOIN environments e   ON e.environment_id = rf.environment_id
        WHERE {" AND ".join(conditions)}
        ORDER BY le.log_timestamp DESC
        LIMIT 500
    """

    logs = db.execute(text(query), params).mappings().all()

    # Dropdown data
    severities = db.execute(text("SELECT severity_code FROM log_severities")).scalars().all()
    categories = db.execute(text("SELECT category_name FROM log_categories")).scalars().all()
    environments = db.execute(text("SELECT environment_code FROM environments")).scalars().all()

    return render_template(
        "view_logs.html",
        logs=logs,
        severities=severities,
        categories=categories,
        environments=environments,
        filters=request.args
    )
