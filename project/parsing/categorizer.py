"""
This is file is to categorize the logs based on keywords present in messages
"""

def resolve_category(message: str) -> str:
    """
    Resolve log category based on message content.
    Order matters: more specific categories first.
    """

    msg = message.lower()

    # ---- AUDIT LOGS (NEW) ----
    # User actions, data changes, access trails
    if any(k in msg for k in [
        "created",
        "updated",
        "deleted",
        "inserted",
        "modified",
        "accessed",
        "viewed",
        "logged in",
        "logged out",
        "password changed",
        "role assigned",
        "permission granted",
        "permission revoked"
    ]):
        return "AUDIT"

    # ---- SECURITY LOGS ----
    if any(k in msg for k in [
        "auth",
        "login",
        "login failed",
        "unauthorized",
        "forbidden",
        "access denied",
        "invalid token",
        "permission denied",
        "password",
        "brute force",
        "clean job startup"
    ]):
        return "SECURITY"

    # ---- APPLICATION LOGS ----
    if any(k in msg for k in [
        "exception",
        "traceback",
        "stack trace",
        "null pointer",
        "runtime error",
        "application",
        "shutdown completed",
        "rate limit",
        "database",
        "application starting",

    ]):
        return "APPLICATION"

    # ---- INFRASTRUCTURE LOGS ----
    if any(k in msg for k in [
        "cpu",
        "memory",
        "disk",
        "filesystem",
        "network",
        "latency",
        "timeout",
        "server down",
        "connection lost"
    ]):
        return "INFRASTRUCTURE"

    # ---- DEFAULT ----
    return "UNCATEGORIZED"
