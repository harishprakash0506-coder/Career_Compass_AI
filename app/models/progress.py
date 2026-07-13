"""
app/models/progress.py
──────────────────────
SQLAlchemy ORM model representing historical Career Readiness parameters
logged daily or weekly to monitor student improvement trends over time.
"""

from datetime import datetime
from app.extensions import db


class StudentProgressLog(db.Model):
    """Logs historic score metrics for a student to show timeline trends."""
    
    __tablename__ = 'student_progress_logs'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    logged_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    career_readiness_score = db.Column(db.Integer, default=0, nullable=False)
    ats_score = db.Column(db.Integer, default=0, nullable=False)
    aptitude_score = db.Column(db.Float, default=0.0, nullable=False)
    coding_score = db.Column(db.Float, default=0.0, nullable=False)
    technical_score = db.Column(db.Float, default=0.0, nullable=False)

    # Relationships
    student = db.relationship('StudentProfile', backref=db.backref('progress_logs', cascade='all, delete-orphan'))
