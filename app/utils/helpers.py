"""
app/utils/helpers.py
─────────────────────
Shared utility functions used across blueprints.
"""

import os
import uuid
from datetime import datetime
from typing import Optional
from werkzeug.utils import secure_filename
from flask import current_app


# ── File Upload ───────────────────────────────────────────────────────────────

def allowed_file(filename: str) -> bool:
    """Return True if the filename has an allowed extension."""
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def save_uploaded_file(file_storage, subfolder: str = '') -> Optional[str]:
    """
    Save a Werkzeug FileStorage object to the configured upload folder.

    Args:
        file_storage: The file from request.files.
        subfolder:    Optional sub-directory within UPLOAD_FOLDER.

    Returns:
        The stored filename (UUID-prefixed) on success, None on failure.
    """
    if not file_storage or not allowed_file(file_storage.filename):
        return None

    original_name = secure_filename(file_storage.filename)
    unique_name   = f'{uuid.uuid4().hex}_{original_name}'

    dest_dir = current_app.config['UPLOAD_FOLDER']
    if subfolder:
        dest_dir = os.path.join(dest_dir, subfolder)
    os.makedirs(dest_dir, exist_ok=True)

    file_storage.save(os.path.join(dest_dir, unique_name))
    return unique_name


# ── Pagination ────────────────────────────────────────────────────────────────

def paginate_query(query, page: int, per_page: int = 10):
    """
    Apply SQLAlchemy pagination to a query.

    Returns a Flask-SQLAlchemy Pagination object.
    """
    return query.paginate(page=page, per_page=per_page, error_out=False)


# ── Date Formatting ───────────────────────────────────────────────────────────

def format_datetime(dt: Optional[datetime], fmt: str = '%d %b %Y') -> str:
    """Format a datetime object; returns '—' for None values."""
    if dt is None:
        return '—'
    return dt.strftime(fmt)


def time_ago(dt: Optional[datetime]) -> str:
    """Return a human-readable 'X time ago' string."""
    if dt is None:
        return '—'
    now  = datetime.utcnow()
    diff = now - dt

    seconds = int(diff.total_seconds())
    if seconds < 60:
        return 'just now'
    minutes = seconds // 60
    if minutes < 60:
        return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
    hours = minutes // 60
    if hours < 24:
        return f'{hours} hour{"s" if hours > 1 else ""} ago'
    days = hours // 24
    if days < 30:
        return f'{days} day{"s" if days > 1 else ""} ago'
    months = days // 30
    if months < 12:
        return f'{months} month{"s" if months > 1 else ""} ago'
    years = days // 365
    return f'{years} year{"s" if years > 1 else ""} ago'


# ── Score Helpers ─────────────────────────────────────────────────────────────

def score_to_color_class(score: float) -> str:
    """Map a 0–100 score to a Bootstrap/custom color class."""
    if score >= 80:
        return 'success'
    if score >= 60:
        return 'info'
    if score >= 40:
        return 'warning'
    return 'danger'


def clamp(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """Clamp a float to [min_val, max_val]."""
    return max(min_val, min(max_val, float(value)))
