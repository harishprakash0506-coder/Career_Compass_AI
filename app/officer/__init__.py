"""app/officer/__init__.py — Placement Officer blueprint definition."""

from flask import Blueprint

officer_bp = Blueprint(
    'officer',
    __name__,
    template_folder='templates',
    url_prefix='/officer',
)

from app.officer import routes  # noqa: F401, E402
from app.officer import scheduler_routes  # noqa: F401, E402

