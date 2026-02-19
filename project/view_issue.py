"""
Importing all the necessary Dependencies
"""

from flask import Blueprint, render_template,redirect,flash,url_for
from flask_login import login_required, current_user
from sqlalchemy import text

from project.db import get_db

view_issues_bp = Blueprint("view-issue", __name__, url_prefix="/view-issues")


@view_issues_bp.route("/" , methods = ['GET'])
@login_required
def view_issues():
    """
    Docstring for view_issues
    """
    if not current_user.is_admin():
        flash("Unauthorized", "danger")
        return redirect(url_for("dashboard"))
    db =get_db()

    reports=db.execute(text(
        """
        select ui.issue_id, ui.user_id, u.username, ui.issue_message, 
        ui.reported_at::timestamp as reported_at 
        from user_issues ui 
        join users u on ui.user_id=u.user_id
        """
    )).fetchall()

    return render_template('view_issues.html',reports=reports)
