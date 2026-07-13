import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve absolute paths
basedir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(basedir, '..'))

# Load .env from project root
load_dotenv(os.path.join(project_root, '.env'))


def _resolve_sqlite_uri(uri: str) -> str:
    if uri and uri.startswith("sqlite:///"):
        path_part = uri[10:]  # remove "sqlite:///"
        if path_part == ":memory:":
            return uri

        # Always resolve relative to the project root
        resolved_path = Path(project_root) / path_part
        resolved_path.parent.mkdir(parents=True, exist_ok=True)

        return "sqlite:///" + resolved_path.as_posix()

    return uri

class Config:
    """Base configuration — shared across all environments."""

    # ── Security ──────────────────────────────────────────────────────────────
    SECRET_KEY: str = os.environ.get(
        'SECRET_KEY', 'dev-insecure-secret-key-must-change-before-production'
    )

    # ── SQLAlchemy ─────────────────────────────────────────────────────────────
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS: dict = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }

    # ── Flask-WTF CSRF ─────────────────────────────────────────────────────────
    WTF_CSRF_ENABLED: bool = True
    WTF_CSRF_TIME_LIMIT: int = 3600  # 1 hour

    # ── File Uploads ───────────────────────────────────────────────────────────
    MAX_CONTENT_LENGTH: int = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16 MB
    UPLOAD_FOLDER: str = os.path.join(project_root, 'uploads')
    ALLOWED_EXTENSIONS: set = {'pdf'}

    # ── ML Models ──────────────────────────────────────────────────────────────
    ML_MODELS_FOLDER: str = os.path.join(project_root, 'ml_models')

    @staticmethod
    def init_app(app) -> None:
        """Perform any app-level initialization required by this config."""
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['ML_MODELS_FOLDER'], exist_ok=True)


class DevelopmentConfig(Config):
    """Development environment — debug on, SQLite dev database."""

    DEBUG: bool = True
    TESTING: bool = False
    SQLALCHEMY_DATABASE_URI: str = _resolve_sqlite_uri(
        os.environ.get(
            'DEV_DATABASE_URL',
            'sqlite:///' + Path(project_root).joinpath('instance', 'careercompass_dev.db').as_posix(),
        )
    )
    SQLALCHEMY_ECHO: bool = False  # Set True to log all SQL statements


class ProductionConfig(Config):
    """Production environment — debug off, stricter settings."""

    DEBUG: bool = False
    TESTING: bool = False
    SQLALCHEMY_DATABASE_URI: str = _resolve_sqlite_uri(
        os.environ.get(
            'DATABASE_URL',
            'sqlite:///' + Path(project_root).joinpath('instance', 'careercompass.db').as_posix(),
        )
    )

    @classmethod
    def init_app(cls, app) -> None:
        Config.init_app(app)
        # Production-only: ensure instance folder is locked down
        import logging
        from logging.handlers import RotatingFileHandler

        logs_dir = os.path.join(project_root, 'logs')
        os.makedirs(logs_dir, exist_ok=True)

        file_handler = RotatingFileHandler(
            os.path.join(logs_dir, 'careercompass.log'),
            maxBytes=10_485_760,   # 10 MB
            backupCount=5,
        )
        file_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('CareerCompass AI startup — Production mode')


class TestingConfig(Config):
    """Testing environment — in-memory SQLite, CSRF disabled."""

    TESTING: bool = True
    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED: bool = False
    MAX_CONTENT_LENGTH: int = 1 * 1024 * 1024  # 1 MB for tests


# ── Config registry ────────────────────────────────────────────────────────────
config: dict = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'testing':     TestingConfig,
    'default':     DevelopmentConfig,
}
