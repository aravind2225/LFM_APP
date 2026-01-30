from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from project.db import get_db

admin_manage_teams_bp = Blueprint("admin_teams", __name__, url_prefix="/admin/teams")


@admin_manage_teams_bp.route("/", methods=["GET"])
@login_required
def list_teams():
    if not current_user.is_admin():
        flash("Unauthorized", "danger")
        return redirect(url_for("dashboard"))

    db = get_db()

    teams=db.execute(text("select team_id, team_name from teams")).fetchall()
    return render_template(
        "admin_manage_teams.html",
        teams=teams
    )

@admin_manage_teams_bp.route("/", methods=["POST"])
@login_required
def add_teams():
    if not current_user.is_admin():
        flash("Unauthorized", "danger")
        return redirect(url_for("dashboard"))

    db = get_db()
    if request.method == "POST":
        tname=request.form.get("team_name")

        db.execute(text(
            "insert into teams(team_name) values(:tname)"
            ),{"tname":tname.upper()})
        
        db.commit()

        flash("Team added Succesfully","success")

        return redirect(url_for('admin_teams.list_teams'))
        






    