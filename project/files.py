from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from sqlalchemy import text
import os
from project.db import get_db
from project.parsing.dispatcher import process_file

files_bp = Blueprint("files", __name__, url_prefix="/files")

ALLOWED_EXTENSIONS = {"TXT", "CSV", "JSON", "XML"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].upper() in ALLOWED_EXTENSIONS


@files_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "GET":
        return render_template("upload.html")

    db = get_db()
    file = request.files.get("file")

    if not file or file.filename == "":
        flash("No file selected", "danger")
        return redirect(request.url)

    if not allowed_file(file.filename):
        flash("File format not allowed", "danger")
        return redirect(request.url)

    filename = file.filename
    extension = filename.rsplit(".", 1)[1].upper()

    env_code = request.form["environment_code"]
    env_row = db.execute(
        text("""
            SELECT environment_id
            FROM environments
            WHERE environment_code = :code
        """),
        {"code": env_code}
    ).mappings().first()

    if not env_row:
        flash("Invalid environment", "danger")
        return redirect(request.url)

    environment_id = env_row["environment_id"]


    try:
        # ---- Get format_id ----
        format_id = db.execute(
            text("""
                SELECT format_id
                FROM file_formats
                WHERE format_name = :fmt
            """),
            {"fmt": extension}
        ).scalar()

        if not format_id:
            flash("Unsupported file format", "danger")
            return redirect(request.url)

        # ---- Get team_id ----
        team_id = db.execute(
        text("""
            SELECT team_id FROM user_teams
            WHERE user_id = :uid order by joined_at desc limit 1
        """),
        {"uid": current_user.id}
        ).scalar()

        if not team_id:
            flash("User not assigned to a team", "danger")
            return redirect(request.url)

        # ---- Read file size ----
        file_bytes = file.read()
        file_size = len(file_bytes)

        # save_path = os.path.join(UPLOAD_FOLDER, filename)
        # file. Save(save_path)

        # ---- Insert into raw_files ----
        result = db.execute(
            text("""
                INSERT INTO raw_files (
                    team_id,
                    uploaded_by,
                    original_name,
                    file_size_bytes,
                    format_id,
                    environment_id
                )
                VALUES (
                    :team_id,
                    :uploaded_by,
                    :original_name,
                    :file_size,
                    :format_id,
                    :environment_id
                )
                RETURNING file_id
            """),
            {
                "team_id": team_id,
                "uploaded_by": current_user.id,
                "original_name": filename,
                "file_size": file_size,
                "format_id": format_id,
                "environment_id": environment_id
            }
        )

        file_id = result.scalar()

        file.seek(0)

        process_file(db, file, extension, file_id)

        db.commit()
        flash("File uploaded and parsed successfully", "success")
        return redirect(url_for("dashboard"))

    except Exception as e:
        db.rollback()
        print("UPLOAD ERROR:", e)
        flash("File upload failed", "danger")
        return redirect(request.url)
