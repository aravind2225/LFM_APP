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
from project.report_issue import user_report_issue_bp
from project.view_issue import view_issues_bp

from project.queries import QUERIES




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
    app.register_blueprint(user_report_issue_bp)
    app.register_blueprint(view_issues_bp)

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
            total_users=db.execute(text(QUERIES["TOTAL_ACTIVE_USERS"])).scalar()
            total_files=db.execute(text(QUERIES["TOTAL_FILES"])).scalar()
            total_logs=db.execute(text(QUERIES["TOTAL_LOGS"])).scalar()
            total_errors=db.execute(text(QUERIES["TOTAL_ERRORS"])).scalar()
            last_file_at=db.execute(text(QUERIES["LAST_FILE_UPLOADED_AT"])).scalar()
            total_archives=db.execute(text(QUERIES["TOTAL_ARCHIVED_FILES"])).scalar()
            total_actions=db.execute(text(QUERIES["TOTAL_ACTIONS"])).scalar()
            biggest_file=db.execute(text(QUERIES["BIGGEST_FILE_NAME"])).scalar()
            avg_logs_per_file=db.execute(text(QUERIES["AVG_LOGS_PER_FILE"])).scalar()
            avg_errors_per_file=db.execute(text(QUERIES['AVG_ERRORS_PER_FILE'])).scalar()
            top_contributor_team=db.execute(text(QUERIES["TOP_CONTRIBUTOR_TEAM"])).scalar()
            top_contributor_user=db.execute(text(QUERIES["TOP_CONTRIBUTOR_USER"])).scalar()
            
            ##charts
            files_by_teams=db.execute(text(QUERIES["FILES_BY_TEAMS"])).fetchall()
            team_names = [row[0] for row in files_by_teams]
            uploads = [row[1] for row in files_by_teams]

            files_by_dates=db.execute(text(QUERIES['FILES_BY_DATES'])).fetchall()
            dates = [row[0].strftime("%Y-%m-%d") for row in files_by_dates]
            date_files_count = [row[1] for row in files_by_dates]

            ##severity analysis.
            slogs=db.execute(text(QUERIES["LOG_SEVERITY_DISTRIBUTION"])).fetchall()
            
            ##users_analytics
            musers=db.execute(text(QUERIES["MOST_ACTIVE_USERS_LAST_7_DAYS"])).fetchall()

            #security_logs_last_week
            seclogs=db.execute(text(QUERIES["SECURITY_LOGS_LAST_WEEK"])).fetchall()

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
                date_files_count=date_files_count,
                slogs=slogs,
                musers=musers,
                seclogs=seclogs
                )
        
        files_self=db.execute(text(QUERIES["FILES_SELF"]),{"uid": current_user.id}).scalar()
        logs_self=db.execute(text(QUERIES["LOGS_SELF"]),{"uid": current_user.id}).scalar()
        errors_self=db.execute(text(QUERIES["ERRORS_SELF"]),{"uid": current_user.id}).scalar()
        last_uploaded=db.execute(text(QUERIES["LAST_UPLOADED_SELF"]),{"uid": current_user.id}).scalar()
        user_team_id = db.execute(
        text(QUERIES["USER_LATEST_TEAM_ID"]),
        {"uid": current_user.id}
        ).scalar()
        files_team=db.execute(text(QUERIES["FILES_TEAM"]),{"tid": user_team_id}).scalar()
        logs_team=db.execute(text(QUERIES["LOGS_TEAM"]),{"tid": user_team_id}).scalar()
        errors_team=db.execute(text(QUERIES["ERRORS_TEAM"]),{"tid": user_team_id}).scalar()
        archives_team=db.execute(text(QUERIES["ARCHIVES_TEAM"]),{"tid": user_team_id}).scalar()
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


