"""
Importing all the necessary Dependencies
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required,current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text

from project.db import get_db
from project.user import AppUser

auth_bp = Blueprint("auth", __name__)


def set_audit_user(db, user_id):
    """
    Docstring for set_audit_user
    
    :param db: to communicate with db
    :param user_id: audit that particular user_id
    """
    db.execute(
        text("SET LOCAL app.current_user_id = :uid"),
        {"uid": user_id}
    )


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Users can register
    """
    if request.method == "POST":
        data = request.form
        db = get_db()

        try:
            if not data.get("role_id") or not data.get("team_id"):
                flash("Role and Team are required", "danger")
                return redirect(url_for("auth.register"))

            password_hash = generate_password_hash(data["password"])

            #insert user data into users table
            result = db.execute(
                text("""
                    INSERT INTO users (
                        first_name, last_name, phone_no,
                        email, username, password_hash,
                        gender
                    )
                    VALUES (
                        :first_name, :last_name, :phone_no,
                        :email, :username, :password_hash,
                        :gender
                    )
                    RETURNING user_id
                """),
                {
                    "first_name": data["first_name"],
                    "last_name": data.get("last_name"),
                    "phone_no": data["phone_no"],
                    "email": data["email"],
                    "username": data.get("username"),
                    "password_hash": password_hash,
                    "gender": data["gender"]
                }
            )


            user_id = result.scalar()
            
            #insert user password and login creds in user_credentials table
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

            #insert user role data into user_roles table
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

            #insert user team data into user_teams table
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
            flash("Registration successful. Please login.", "success")
            return redirect(url_for("auth.login"))

        #catch the error and rolling back if any error occurs meanwhile
        except Exception as e:
            db.rollback()
            print("REGISTER ERROR:", e)
            flash("Registration failed. Check inputs.", "danger")
            return redirect(url_for("auth.register"))
    
    db = get_db()
    team_names=db.execute(text("select team_id, team_name from teams")).fetchall()

    # Returning the template register.html 
    # and passing team names in our DB to show in team selection dropdown
    return render_template(
        "register.html",
        team_names=team_names
        )



@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Method for login
    """
    if request.method == "POST":
        data = request.form
        db = get_db()

        #fetching data of the user who tries to login
        user = db.execute(
            text("""
                SELECT u.user_id, u.password_hash, u.is_active,
                       c.failed_attempts, c.is_locked, c.locked_until
                FROM users u
                JOIN user_credentials c ON c.user_id = u.user_id
                WHERE u.email = :login OR u.username = :login
            """),
            {"login": data["login"]}
        ).mappings().first()

        if not user:
            flash("Wrong credentials", "danger")
            return redirect(url_for("auth.login"))
        
        


        # Check lock
        if user["is_locked"]:
            locked = db.execute(
                text("""
                    SELECT locked_until > NOW()
                    FROM user_credentials
                    WHERE user_id = :uid
                """),
                {"uid": user["user_id"]}
            ).scalar()

            if locked:
                flash("Account locked. Try again after 30 minutes.", "danger")
                return redirect(url_for("auth.login"))


        # Password check
        if not check_password_hash(user["password_hash"], data["password"]):
            failed = user["failed_attempts"] + 1

            if failed >= 5:
                db.execute(
                    text("""
                        UPDATE user_credentials
                        SET failed_attempts = :fa,
                            is_locked = TRUE,
                            locked_until = NOW() + INTERVAL '30 minutes'
                        WHERE user_id = :uid
                    """),
                    {"fa": failed, "uid": user["user_id"]}
                )
            else:
                db.execute(
                    text("""
                        UPDATE user_credentials
                        SET failed_attempts = :fa,
                            last_failed_at = NOW()
                        WHERE user_id = :uid
                    """),
                    {"fa": failed, "uid": user["user_id"]}
                )

            db.commit()
            flash("Wrong credentials", "danger")
            return redirect(url_for("auth.login"))

        # SUCCESSFUL LOGIN → reset attempts
        if not user["is_active"]:

            flash("Sorry!! You are Deactivated by Admins", "danger")
            return redirect(url_for("auth.login"))
        

        db.execute(
            text("""
                UPDATE user_credentials
                SET failed_attempts = 0,
                    is_locked = FALSE,
                    locked_until = NULL
                WHERE user_id = :uid
            """),
            {"uid": user["user_id"]}
        )

        app_user = AppUser.get(user["user_id"])
        login_user(app_user)

        db.execute(
            text("SET LOCAL app.current_user_id = :uid"),
            {"uid": user["user_id"]}
        )

        db.commit()
        return redirect(url_for("dashboard"))

    return render_template("login.html")




@auth_bp.route("/logout")
@login_required
def logout():
    """
    Docstring for logout
    The user will be logged out if this method is called
    """
    logout_user()
    flash("You are logged out", "info")
    return redirect(url_for("index"))

