"""
run.py
───────
Application entry point.

Usage (development):
    python run.py

Usage (production with gunicorn):
    gunicorn -w 4 -b 0.0.0.0:5000 "run:app"
"""

import os
import mimetypes
from dotenv import load_dotenv

# Ensure correct MIME types on Windows
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('application/javascript', '.js')

# Load .env BEFORE importing app so config classes pick up env vars
load_dotenv()

from app import create_app          # noqa: E402
from app.extensions import db       # noqa: E402

config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

# ── Auto-create all database tables on first run ──────────────────────────────
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config.get('DEBUG', True),
    )
