"""
app/utils/decorators.py
────────────────────────
Custom route decorators for role-based access control.

Usage:
    @login_required
    @role_required(Role.ADMIN)
    def admin_only_view():
        ...
"""

from functools import wraps
from flask import abort
from flask_login import current_user


def role_required(*roles: str):
    """
    Decorator factory that restricts a route to one or more roles.

    If the authenticated user's role is not in the allowed list,
    Flask aborts with 403 Forbidden.

    Args:
        *roles: One or more role strings from app.models.user.Role.

    Example:
        @role_required(Role.ADMIN, Role.OFFICER)
        def view(): ...
    """
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return func(*args, **kwargs)
        return decorated_function
    return decorator


def student_required(func):
    """Shorthand: restrict to role=student."""
    from app.models.user import Role
    return role_required(Role.STUDENT)(func)


def officer_required(func):
    """Shorthand: restrict to role=officer."""
    from app.models.user import Role
    return role_required(Role.OFFICER)(func)


def admin_required(func):
    """Shorthand: restrict to role=admin."""
    from app.models.user import Role
    return role_required(Role.ADMIN)(func)
