"""
app/models/user.py
──────────────────
User account model with role-based access control.
Roles: student | officer | admin
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager


class Role:
    """Namespace for user role constants."""

    STUDENT = 'student'
    OFFICER = 'officer'   # Placement Officer
    ADMIN   = 'admin'
    ALL     = [STUDENT, OFFICER, ADMIN]


class User(UserMixin, db.Model):
    """
    Core authentication and identity model.

    One User → one StudentProfile (for role=student).
    Officers and Admins do not have a StudentProfile.
    """

    __tablename__ = 'users'

    # ── Primary Key ─────────────────────────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)

    # ── Identity ────────────────────────────────────────────────────────────────
    full_name    = db.Column(db.String(120), nullable=False)
    email        = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    # ── Role & Status ───────────────────────────────────────────────────────────
    role      = db.Column(db.String(20), nullable=False, default=Role.STUDENT)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # ── Timestamps ──────────────────────────────────────────────────────────────
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # ── Relationships ────────────────────────────────────────────────────────────
    student_profile = db.relationship(
        'StudentProfile',
        backref='user',
        uselist=False,
        cascade='all, delete-orphan',
        lazy='select',
    )

    # ── Password Helpers ─────────────────────────────────────────────────────────
    def set_password(self, password: str) -> None:
        """Hash and store password. Never stores plain-text."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a plain-text password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    # ── Role Helpers ─────────────────────────────────────────────────────────────
    @property
    def is_student(self) -> bool:
        return self.role == Role.STUDENT

    @property
    def is_officer(self) -> bool:
        return self.role == Role.OFFICER

    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN

    # ── Flask-Login Required ─────────────────────────────────────────────────────
    def get_id(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return f'<User id={self.id} email={self.email!r} role={self.role!r}>'


# ── Flask-Login user loader ──────────────────────────────────────────────────────
@login_manager.user_loader
def load_user(user_id: str):
    """Load user by primary key for session management."""
    return User.query.get(int(user_id))
