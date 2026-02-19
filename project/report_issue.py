"""
Importing all the necessary Dependencies
"""

from flask import Blueprint, render_template, request,flash
from flask_login import login_required, current_user
from sqlalchemy import text

from project.db import get_db

user_report_issue_bp=Blueprint("report-issue", __name__, url_prefix="/report-issue")

@user_report_issue_bp.route('/',methods=["GET", "POST"])
@login_required
def report_issue():
    """
    Docstring for report_issue
    """
    db=get_db()

    if request.method=='POST':
        data=request.form
        db.execute(text(
            """
            insert into user_issues(
            user_id,issue_message
            )
            values(
            :uid,:issue)

            """
        ),{
            'uid':current_user.id, 'issue':data['message']
        })

        db.commit()
        flash('Your issue reported successfully','success')

    return render_template('report_issue.html')
