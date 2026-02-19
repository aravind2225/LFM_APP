"""
Importing all the dependencies
"""

from flask import Blueprint, render_template, request,flash
from flask_login import login_required, current_user
from sqlalchemy import text

from project.db import get_db

admin_del_bp = Blueprint("admin-del", __name__, url_prefix="/admin-del")



@admin_del_bp.route("/admin-del", methods=["GET", "POST"])
@login_required
def del_files():
    """
    Docstring for del_files
    Admin can delete logs and files uploaded any one
    """
    db = get_db()

    if request.method == "POST":
        global_file_id=request.form.get('global_file_id',type=int)

        all_file_ids=db.execute(
        text("SELECT file_id FROM raw_files")
        ).scalars().all()

        if global_file_id in all_file_ids:
            db.execute(
                text("DELETE FROM log_entries WHERE file_id = :file_id"),
                {"file_id": global_file_id}
            )
            db.execute(
                text("DELETE FROM raw_files WHERE file_id = :file_id"),
                {"file_id": global_file_id}
            )
            db.commit()
            flash("File delted succesfully", "success")


        else:
            flash("File does not exits", "danger")



    your_files = db.execute(
        text(
            """SELECT file_id, original_name, u.username as uname 
            FROM raw_files rf 
            join users u on rf.uploaded_by=u.user_id 
            WHERE uploaded_by = :uid"""),
        {"uid": current_user.id}
    ).fetchall()

    all_files = db.execute(text("""SELECT file_id, original_name, u.username as uname
                                FROM raw_files rf 
                                join users u on rf.uploaded_by=u.user_id""")).fetchall()

    return render_template("admin_delete.html", files=your_files,all_files=all_files)
