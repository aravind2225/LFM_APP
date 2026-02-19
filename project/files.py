"""
Importing all the necessary Dependencies
"""

from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from sqlalchemy import text
import os
from project.db import get_db
from project.parsing.dispatcher import process_file
import hashlib

files_bp = Blueprint("files", __name__, url_prefix="/files")

ALLOWED_EXTENSIONS = {"TXT", "CSV", "JSON", "XML"}


def allowed_file(filename: str) -> bool:
    """
    Docstring for allowed_file
    to check whether the file is allowed or not

    :param filename: filename as input 
    :type filename: str
    :return: if it allowed or not
    :rtype: bool
    """
    return "." in filename and filename.rsplit(".", 1)[1].upper() in ALLOWED_EXTENSIONS

def calculate_checksum(file_obj, algorithm="sha256"):
    """
    Docstring for calculate_checksum
    
    :param file_obj: file that is being uploaded by user
    :param algorithm: sha256 algorithm is used
    """
    hash_obj = hashlib.new(algorithm)

    file_obj.seek(0)  # Ensure pointer at start

    while chunk := file_obj.read(8192):
        hash_obj.update(chunk)

    file_obj.seek(0)  # Reset pointer for future usage
    return hash_obj.hexdigest()

@files_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """
    user can upload multiple files of different formats
    """

    if request.method == "GET":
        return render_template("upload.html")

    db = get_db()

    files = request.files.getlist("files")
    print("fgdf",files)

    if not files or files[0].filename == "":
        flash("No files selected", "danger")
        return redirect(request.url)

    # ----------------------------
    # Environment selection (same for all files)
    # ----------------------------
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

    # ----------------------------
    # Get user's latest team
    # ----------------------------
    team_id = db.execute(
        text("""
            SELECT team_id
            FROM user_teams
            WHERE user_id = :uid
            ORDER BY joined_at DESC
            LIMIT 1
        """),
        {"uid": current_user.id}
    ).scalar()

    if not team_id:
        flash("User not assigned to a team", "danger")
        return redirect(request.url)

    success_count = 0
    fail_count = 0
    all_file_checksums=db.execute(text("select file_hash from raw_files")).scalars().all()

    # ==========================================================
    # Process each file
    # ==========================================================
    for file in files:
        print("File I",file)

        if not file or file.filename == "":
            continue

        if not allowed_file(file.filename):
            fail_count += 1
            continue

        filename = file.filename
        extension = filename.rsplit(".", 1)[1].upper()

        checksum=calculate_checksum(file)
        if checksum in all_file_checksums:
            flash('Duplicate File Detected','danger')
        else:
            try:
                # ----------------------------
                # Get format_id
                # ----------------------------
                format_id = db.execute(
                    text("""
                        SELECT format_id
                        FROM file_formats
                        WHERE format_name = :fmt
                    """),
                    {"fmt": extension}
                ).scalar()

                if not format_id:
                    fail_count += 1
                    continue

                # ----------------------------
                # Read file size
                # ----------------------------
                file_bytes = file.read()
                file_size = len(file_bytes)

                # ----------------------------
                # Insert raw_files row
                # ----------------------------
                result = db.execute(
                    text("""
                        INSERT INTO raw_files (
                            team_id,
                            uploaded_by,
                            original_name,
                            file_size_bytes,
                            format_id,
                            environment_id,
                            file_hash
                        )
                        VALUES (
                            :team_id,
                            :uploaded_by,
                            :original_name,
                            :file_size,
                            :format_id,
                            :environment_id,
                            :file_hash
                        )
                        RETURNING file_id
                    """),
                    {
                        "team_id": team_id,
                        "uploaded_by": current_user.id,
                        "original_name": filename,
                        "file_size": file_size,
                        "format_id": format_id,
                        "environment_id": environment_id,
                        "file_hash":checksum
                    }
                )

                file_id = result.scalar()

                # Reset pointer before parsing
                file.seek(0)

                # ----------------------------
                # Existing parsing pipeline
                # ----------------------------
                clean_entries,total_logs=process_file(db, file, extension, file_id)

                success_count += 1

            except Exception as e:
                print("UPLOAD ERROR:", e)
                db.rollback()
                fail_count += 1
                continue

    db.commit()

    flash(f"{success_count} files uploaded successfully with {len(clean_entries)}/{total_logs} logs parsed", "success")

    if fail_count:
        flash(f"{fail_count} files failed", "warning")

    return redirect(url_for("dashboard"))
