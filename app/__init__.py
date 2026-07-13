"""
app/__init__.py
────────────────
Application Factory — create_app(config_name).

All Flask extensions, blueprints, error handlers, and shell context
are wired here. Import and use create_app() in run.py and tests.
"""

import os
from flask import Flask, render_template
from app.config import config
from app.extensions import db, login_manager, migrate, csrf


def create_app(config_name: str = 'default') -> Flask:
    """
    Create and configure a Flask application instance.

    Args:
        config_name: One of 'development', 'production', 'testing', 'default'.

    Returns:
        Fully configured Flask application.
    """
    app = Flask(__name__, instance_relative_config=True)

    # ── Load Config ──────────────────────────────────────────────────────────────
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # ── Ensure Instance Folder Exists ────────────────────────────────────────────
    os.makedirs(app.instance_path, exist_ok=True)

    # ── Initialise Extensions ────────────────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # ── Register All ORM Models ──────────────────────────────────────────────────
    # Must be imported before db.create_all() so SQLAlchemy sees every table.
    with app.app_context():
        from app.models import (  # noqa: F401
            User, StudentProfile, PlacementRecord, ResumeAnalysis,
            Question, Assessment,
        )

    # ── Register Blueprints ──────────────────────────────────────────────────────
    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.student import student_bp
    app.register_blueprint(student_bp, url_prefix='/student')

    from app.officer import officer_bp
    app.register_blueprint(officer_bp, url_prefix='/officer')

    from app.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # ── Root Route ───────────────────────────────────────────────────────────────
    @app.route('/')
    def index():
        return render_template('index.html')

    # ── Error Handlers ───────────────────────────────────────────────────────────
    @app.errorhandler(403)
    def forbidden(exc):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(exc):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(exc):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # ── Shell Context ────────────────────────────────────────────────────────────
    @app.shell_context_processor
    def make_shell_context():
        from app.models import (
            User, StudentProfile, PlacementRecord,
            ResumeAnalysis, Question, Assessment,
        )
        return {
            'db': db,
            'User': User,
            'StudentProfile': StudentProfile,
            'PlacementRecord': PlacementRecord,
            'ResumeAnalysis': ResumeAnalysis,
            'Question': Question,
            'Assessment': Assessment,
        }

    return app
