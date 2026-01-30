from flask import Flask, render_template,session
from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user,login_required
from flask_login import LoginManager
from sqlalchemy import text

from project.config import Config
from project.db import init_db, db_session,get_db
from project.auth import auth_bp
from project.user import AppUser
from project.files import files_bp
from project.logs import logs_bp
from project.delete import del_bp
from project.admin_logs import admin_logs_bp
from project.admin_delete import admin_del_bp
from project.admin_security_logs import admin_security_logs_bp
from project.admin_manage_users import admin_manage_users_bp
from project.admin_archive_files import archive_file_bp
from project.admin_manage_teams import admin_manage_teams_bp
from project.profile import user_view_profile_bp




def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_db(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return AppUser.get(int(user_id))
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(logs_bp)
    app.register_blueprint(del_bp)
    app.register_blueprint(admin_logs_bp)
    app.register_blueprint(admin_del_bp)
    app.register_blueprint(admin_security_logs_bp)
    app.register_blueprint(admin_manage_users_bp)
    app.register_blueprint(archive_file_bp)
    app.register_blueprint(admin_manage_teams_bp)
    app.register_blueprint(user_view_profile_bp)

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        # return redirect(url_for("auth.login"))
        return render_template("home_page.html")

    @app.route("/dashboard")
    @login_required
    def dashboard():
        db=get_db()
        if current_user.is_admin():
            total_users=db.execute(text("select count(*) from users where is_active=true")).scalar()
            total_files=db.execute(text("select count(*) from raw_files where is_archived=false")).scalar()
            total_logs=db.execute(text("select count(*) from log_entries le join raw_files rf on le.file_id=rf.file_id where rf.is_archived=false")).scalar()
            total_errors=db.execute(text("select count(*) from log_entries le join raw_files rf on le.file_id=rf.file_id where rf.is_archived=false and le.severity_id=4")).scalar()
            last_file_at=db.execute(text("select coalesce(max(uploaded_at)::timestamp,'2035-01-01 00:00:00+00'::timestamp) from raw_files")).scalar()
            total_archives=db.execute(text("select count(*) from raw_files where is_archived=true")).scalar()
            total_actions=db.execute(text("select count(*) from audit_trail")).scalar()
            biggest_file=db.execute(text("select original_name from raw_files where file_size_bytes=(select max(file_size_bytes) from raw_files where is_archived=false)")).scalar()
            avg_logs_per_file=db.execute(text("select round(count(*)::decimal/nullif((count( distinct rf.file_id)),0),2) from log_entries le join raw_files rf on le.file_id=rf.file_id where rf.is_archived=false")).scalar()
            avg_errors_per_file=db.execute(text("select round(count(*)::decimal/nullif((count( distinct rf.file_id)),0),2) from log_entries le join raw_files rf on le.file_id=rf.file_id where rf.is_archived=false and le.severity_id=4")).scalar()
            top_contributor_team=db.execute(text("select t.team_name  from raw_files rf join teams t on t.team_id=rf.team_id group by t.team_name order by count(*)")).scalar()
            top_contributor_user=db.execute(text("select u.username  from raw_files rf join users u on u.user_id=rf.uploaded_by group by u.username order by count(*)")).scalar()
            
            ##charts
            files_by_teams=db.execute(text("select t.team_name,count(*) as total_uploads from raw_files rf join teams t on rf.team_id=t.team_id group by t.team_name")).fetchall()
            team_names = [row[0] for row in files_by_teams]
            uploads = [row[1] for row in files_by_teams]

            files_by_dates=db.execute(text("select date(uploaded_at) as date,count(*) as total_files from raw_files group by date(uploaded_at) order by date(uploaded_at)")).fetchall()
            dates = [row[0].strftime("%Y-%m-%d") for row in files_by_dates]
            date_files_count = [row[1] for row in files_by_dates]
            return render_template(
                "admin_dashboard.html",
                total_users=total_users,
                total_files=total_files,
                total_logs=total_logs,
                total_errors=total_errors,
                last_file_at=last_file_at,
                total_archives=total_archives,
                total_actions=total_actions,
                biggest_file=biggest_file,
                avg_logs_per_file=avg_logs_per_file,
                avg_errors_per_file=avg_errors_per_file,
                top_contributor_team=top_contributor_team,
                top_contributor_user=top_contributor_user,
                team_names=team_names,
                uploads=uploads,
                dates=dates,
                date_files_count=date_files_count
                )
        
        files_self=db.execute(text("select count(*) from raw_files where uploaded_by=:uid and is_archived=false"),{"uid": current_user.id}).scalar()
        logs_self=db.execute(text("select count(*) from log_entries le join raw_files rf on le.file_id=rf.file_id where rf.uploaded_by=:uid and rf.is_archived=false"),{"uid": current_user.id}).scalar()
        errors_self=db.execute(text("select count(*) from log_entries le join raw_files rf on le.file_id=rf.file_id where rf.uploaded_by=:uid and severity_id=4 and rf.is_archived=false "),{"uid": current_user.id}).scalar()
        last_uploaded=db.execute(text("select coalesce(max(uploaded_at),'2035-01-01 00:00:00+00'::timestamptz) from raw_files where uploaded_by=:uid"),{"uid": current_user.id}).scalar()
        user_team_id = db.execute(
        text("""
            SELECT team_id FROM user_teams
            WHERE user_id = :uid order by joined_at desc limit 1
        """),
        {"uid": current_user.id}
        ).scalar()
        files_team=db.execute(text("select count(*) from raw_files where team_id=:tid and is_archived=false"),{"tid": user_team_id}).scalar()
        logs_team=db.execute(text("select count(*) from log_entries le join raw_files rf on le.file_id=rf.file_id where rf.team_id=:tid and rf.is_archived=false"),{"tid": user_team_id}).scalar()
        errors_team=db.execute(text("select count(*) from log_entries le join raw_files rf on le.file_id=rf.file_id where rf.team_id=:tid and severity_id=4 and rf.is_archived=false"),{"tid": user_team_id}).scalar()
        archives_team=db.execute(text("select count(*) from raw_files where is_archived=true and team_id=:tid"),{"tid": user_team_id}).scalar()
        return render_template(
            "user_dashboard.html",
            files_self=files_self,
            logs_self=logs_self,
            errors_self=errors_self,
            last_uploaded=last_uploaded,
            files_team=files_team,
            logs_team=logs_team,
            errors_team=errors_team,
            archives_team=archives_team
            )
    
    @app.before_request
    def set_audit_user_context():
        """
        Make current user_id visible to PostgreSQL triggers.
        This runs on EVERY request and is connection-safe.
        """
        if current_user.is_authenticated:
            db_session.execute(
                text("SET app.current_user_id = :uid"),
                {"uid": current_user.id}
            )


    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app


