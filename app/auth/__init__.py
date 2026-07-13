"""app/auth/__init__.py — Auth blueprint definition."""

from flask import Blueprint

auth_bp = Blueprint(
    'auth',
    __name__,
    template_folder='templates',
    url_prefix='/auth',
)

from app.auth import routes  # noqa: F401, E402 — registers route handlers
