"""
Importing all the dependencies
"""

from flask import Blueprint, render_template, request,redirect,flash,url_for
from flask_login import login_required, current_user
from sqlalchemy import text

from project.db import get_db

archive_file_bp = Blueprint("archive-files", __name__, url_prefix="/archive-files")


@archive_file_bp.route("/" , methods = ['GET'])
@login_required
def list_files():
    """
    Docstring for list_files
    This is the method list the files
    """

    if not current_user.is_admin():
        flash("Unauthorized", "danger")
        return redirect(url_for("dashboard"))
    db =get_db()

    files=db.execute(text(
        """select rf.file_id, rf.original_name, u.username,
        rf.uploaded_at::date as dt, rf.is_archived
        from raw_files rf join users u on rf.uploaded_by=u.user_id"""
    )).fetchall()

    return render_template(
        'admin_archive_file.html',
        files=files
    )

@archive_file_bp.route("/archive/<int:file_id>" , methods = ['POST'])
@login_required
def archive(file_id):
    """
    Docstring for archive
    
    :param file_id: file_id is the id of file which we need to archive
    """
    if not current_user.is_admin():
        flash("Unauthorized", "danger")
        return redirect(url_for("dashboard"))
    
    db =get_db()

    #Toggling the archive status of file
    db.execute(text(
        "update raw_files set is_archived = NOT is_archived where file_id=:file_id"
    ),{"file_id":file_id})

    db.commit()
    flash("File status updated", "success")
    return redirect(url_for('archive-files.list_files'))