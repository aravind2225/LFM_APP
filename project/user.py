from flask_login import UserMixin
from sqlalchemy import text
from project.db import get_db


class AppUser(UserMixin):
    def __init__(self, user_id, username, role):
        self.id = user_id
        self.username = username
        self.role = role

    @staticmethod
    def get(user_id):
        db = get_db()
        row = db.execute(
            text("""
                SELECT u.user_id, u.username, r.role_name
                FROM users u
                JOIN user_roles ur ON ur.user_id = u.user_id
                JOIN roles r ON r.role_id = ur.role_id
                WHERE u.user_id = :uid
            """),
            {"uid": user_id}
        ).mappings().first()

        if not row:
            return None

        return AppUser(
            user_id=row["user_id"],
            username=row["username"],
            role=row["role_name"]
        )

    def is_admin(self):
        return self.role == "ADMIN"

