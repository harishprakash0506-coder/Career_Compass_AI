"""
extensions.py
─────────────
Instantiates all Flask extensions as module-level singletons.
Extensions are configured (via .init_app) inside the application factory
in app/__init__.py — NOT here — to support the Application Factory pattern
and avoid circular imports.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

# ── SQLAlchemy ORM ─────────────────────────────────────────────────────────────
db = SQLAlchemy()

# ── Flask-Login ────────────────────────────────────────────────────────────────
login_manager = LoginManager()
login_manager.login_view = 'auth.login'          # Redirect target for @login_required
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'
login_manager.session_protection = 'strong'

# ── Flask-Migrate (Alembic) ────────────────────────────────────────────────────
migrate = Migrate()

# ── Flask-WTF CSRF Protection ──────────────────────────────────────────────────
csrf = CSRFProtect()
