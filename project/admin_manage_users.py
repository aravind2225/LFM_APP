"""
Importing all the necessary Dependencies
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from project.db import get_db

admin_manage_users_bp = Blueprint("admin_users", __name__, url_prefix="/admin/users")


@admin_manage_users_bp.route("/", methods=["GET"])
@login_required
def list_users():
    if not current_user.is_admin():
        flash("Unauthorized", "danger")
        return redirect(url_for("dashboard"))

    db = get_db()

    users = db.execute(text("""
        SELECT
            u.user_id,
            u.first_name,
            u.last_name,
            u.email,
            u.username,
            u.is_active,
            r.role_name
        FROM users u
        JOIN user_roles ur ON ur.user_id = u.user_id
        JOIN roles r ON r.role_id = ur.role_id
        -- WHERE u.is_deleted = FALSE
        ORDER BY u.created_at DESC
    """)).mappings().all()

    return render_template("admin_manage_users.html", users=users)

@admin_manage_users_bp.route("/toggle/<int:user_id>", methods=["POST"])
@login_required
def toggle_user(user_id):
    if not current_user.is_admin():
        flash("Unauthorized", "danger")
        return redirect(url_for("dashboard"))

    if user_id == current_user.id:
        flash("You cannot deactivate yourself", "danger")
        return redirect(url_for("admin_users.list_users"))

    db = get_db()

    db.execute(text("""
        UPDATE users
        SET is_active = NOT is_active
        WHERE user_id = :uid
    """), {"uid": user_id})

    db.commit()
    flash("User status updated", "success")
    return redirect(url_for("admin_users.list_users"))


@admin_manage_users_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_user():
    if not current_user.is_admin():
        flash("Unauthorized", "danger")
        return redirect(url_for("dashboard"))

    db = get_db()

    if request.method == "POST":
        data = request.form
        password_hash = generate_password_hash(data["password"])
        #admins can create a new user
        try:
            result = db.execute(text("""
                INSERT INTO users (
                    first_name, last_name, phone_no,
                    email, username, password_hash, gender
                )
                VALUES (
                    :first, :last, :phone,
                    :email, :username, :password, :gender
                )
                RETURNING user_id
            """), {
                "first": data["first_name"],
                "last": data["last_name"],
                "phone": data["phone_no"],
                "email": data["email"],
                "username": data["username"],
                "password": password_hash,
                "gender": data["gender"]
            })

            user_id = result.scalar()
            #inserting those user credentials
            db.execute(
                text("""
                    INSERT INTO user_credentials (
                        user_id,
                        failed_attempts,
                        is_locked,
                        password_set_at
                    )
                    VALUES (:uid, 0, FALSE, NOW())
                """),
                {"uid": user_id}
            )
            #inserting into user_roles table
            db.execute(
                text("""
                    INSERT INTO user_roles (user_id, role_id)
                    VALUES (:uid, :rid)
                """),
                {
                    "uid": user_id,
                    "rid": int(data["role_id"])
                }
            )
            #inserting into user_teams table
            db.execute(
                text("""
                    INSERT INTO user_teams (user_id, team_id)
                    VALUES (:user_id, :team_id)
                """),
                {
                    "user_id": user_id,
                    "team_id": int(data["team_id"])
                }
            )

            db.commit()
            flash("User created successfully", "success")
            return redirect(url_for("admin_users.list_users"))

        except Exception as e:
            db.rollback()
            flash(str(e), "danger")
    team_names=db.execute(text("select team_id, team_name from teams")).fetchall()
    return render_template("admin_manage_users_create.html", mode="create",team_names=team_names)


@admin_manage_users_bp.route("/edit/<int:user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    if not current_user.is_admin():
        flash("Unauthorized", "danger")
        return redirect(url_for("dashboard"))

    db = get_db()

    # ----------------------------
    # Fetch user
    # ----------------------------
    user = db.execute(
        text("""
            SELECT *
            FROM users
            WHERE user_id = :uid
              AND is_active = TRUE
        """),
        {"uid": user_id}
    ).mappings().first()

    if not user:
        flash("User not found", "danger")
        return redirect(url_for("admin_users.list_users"))

    # ----------------------------
    # Current (latest) team
    # ----------------------------
    current_team_id = db.execute(
        text("""
            SELECT team_id
            FROM user_teams
            WHERE user_id = :uid
            ORDER BY joined_at DESC
            LIMIT 1
        """),
        {"uid": user_id}
    ).scalar()

    # ----------------------------
    # All teams (for dropdown)
    # ----------------------------
    teams = db.execute(
        text("SELECT team_id, team_name FROM teams ORDER BY team_name")
    ).mappings().all()

    if request.method == "POST":
        data = request.form
        new_team_id = int(data["team_id"])

        try:
            # 1️⃣ Update basic user profile
            db.execute(
                text("""
                    UPDATE users
                    SET
                        first_name = :first,
                        last_name  = :last,
                        phone_no   = :phone,
                        email      = :email,
                        username   = :username,
                        gender     = :gender,
                        updated_at = NOW()
                    WHERE user_id = :uid
                """),
                {
                    "first": data["first_name"],
                    "last": data.get("last_name"),
                    "phone": data["phone_no"],
                    "email": data["email"],
                    "username": data["username"],
                    "gender": data["gender"],
                    "uid": user_id
                }
            )

            # 2️⃣ Add new team mapping (history preserved)
            db.execute(
                text("""
                    INSERT INTO user_teams (user_id, team_id)
                    VALUES (:uid, :tid)
                    ON CONFLICT DO NOTHING
                """),
                {
                    "uid": user_id,
                    "tid": new_team_id
                }
            )

            db.commit()
            flash("User updated successfully", "success")
            return redirect(url_for("admin_users.list_users"))

        except Exception as e:
            db.rollback()
            flash(str(e), "danger")

    return render_template(
        "admin_manage_users_create.html",
        user=user,
        mode="edit",
        team_names=teams,
        current_team_id=current_team_id
    )
