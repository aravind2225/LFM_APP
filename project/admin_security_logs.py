from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import text

from project.db import get_db

admin_security_logs_bp = Blueprint("admin-security-logs", __name__, url_prefix="/admin-security-logs")


@admin_security_logs_bp.route("/admin-security-view", methods=["GET"])
@login_required
def view_security_logs():
    db = get_db()

    audits=db.execute(text("SELECT a.action_id,u.username, a.action_type, a.action_time::timestamp(0) as audit_time FROM audit_trail a join users u on a.user_id=u.user_id order by audit_time desc")).fetchall()

    return render_template(
        "admin_security_logs.html",audits=audits
    )
