from flask import Blueprint, render_template, request,flash,redirect,url_for
from flask_login import login_required, current_user
from sqlalchemy import text

from project.db import get_db

user_view_profile_bp=Blueprint("profile", __name__, url_prefix="/profile")


@user_view_profile_bp.route('/')
@login_required
def view_profile():
    db=get_db()

    user_team_id = db.execute(
        text("""
            SELECT team_id FROM user_teams
            WHERE user_id = :uid order by joined_at desc limit 1
        """),
        {"uid": current_user.id}
    ).scalar()
    user_info=db.execute(text("""
    select 
    u.user_id,
    u.username,
    u.first_name,
    u.last_name,
    u.phone_no,
    u.email,
    u.gender,
    r.role_name,
    t.team_name,
    u.created_at
    from users u join user_teams ut on u.user_id=ut.user_id
    join user_roles ur on ur.user_id=u.user_id 
    join roles r on r.role_id=ur.role_id
    join teams t on t.team_id=ut.team_id
    where u.user_id=:uid
    order by ut.joined_at desc limit 1;
    """),{"uid":current_user.id}).fetchone()
    
    return render_template("profile.html",user_info=user_info)
    

    

