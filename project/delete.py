"""
Importing all the necessary Dependencies
"""

from flask import Blueprint, render_template, request,flash
from flask_login import login_required, current_user
from sqlalchemy import text

from project.db import get_db

del_bp = Blueprint("del", __name__, url_prefix="/del")



@del_bp.route("/", methods=["GET", "POST"])
@login_required
def del_files():
    """
    Docstring for del_files
    End Users can only delete the files they have uploaded
    """
    db = get_db()

    if request.method == "POST":
        file_id = request.form.get('file_id',type=int)

        file_ids=db.execute(
        text("SELECT file_id FROM raw_files WHERE uploaded_by = :uid"),
        {"uid": current_user.id}
        ).scalars().all()


        if file_id in file_ids:
            db.execute(
                text("DELETE FROM log_entries WHERE file_id = :file_id"),
                {"file_id": file_id}
            )
            db.execute(
                text("DELETE FROM raw_files WHERE file_id = :file_id"),
                {"file_id": file_id}
            )
            db.commit()
            flash("File Deleted succesfully.", "success")
        else:
            flash("Either file does not exits or not uploaded by you.", "danger")


    files = db.execute(
        text("SELECT file_id, original_name FROM raw_files WHERE uploaded_by = :uid"),
        {"uid": current_user.id}
    ).fetchall()

    return render_template("delete.html", files=files)
