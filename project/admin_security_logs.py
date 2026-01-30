from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import text

from project.db import get_db

admin_security_logs_bp = Blueprint("admin-security-logs", __name__, url_prefix="/admin-security-logs")


@admin_security_logs_bp.route("/admin-security-view", methods=["GET"])
@login_required
def view_security_logs():
    db = get_db()

    audits=db.execute(text("SELECT action_id,user_id, action_type, action_time FROM audit_trail")).fetchall()

    return render_template(
        "admin_security_logs.html",audits=audits
    )
