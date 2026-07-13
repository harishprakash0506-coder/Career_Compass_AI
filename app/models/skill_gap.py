"""
app/models/skill_gap.py
───────────────────────
SQLAlchemy ORM model representing historic Skill Gap Analysis records.
"""

import json
from datetime import datetime
from app.extensions import db


class SkillGapAnalysis(db.Model):
    """Stores history of skill gap analysis comparisons for students."""
    
    __tablename__ = 'skill_gap_analyses'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    target_role = db.Column(db.String(100), nullable=False)
    target_company = db.Column(db.String(100), nullable=True)
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Store lists/dictionaries as JSON columns
    _strong_skills = db.Column('strong_skills', db.Text, default='[]', nullable=False)
    _weak_skills = db.Column('weak_skills', db.Text, default='[]', nullable=False)
    _missing_skills = db.Column('missing_skills', db.Text, default='[]', nullable=False)
    _recommendations = db.Column('recommendations', db.Text, default='{}', nullable=False)

    # Relationships
    student = db.relationship('StudentProfile', backref=db.backref('skill_gaps', cascade='all, delete-orphan'))

    # Getter/setter properties for JSON deserialization
    @property
    def strong_skills(self) -> list:
        try:
            return json.loads(self._strong_skills)
        except Exception:
            return []

    @strong_skills.setter
    def strong_skills(self, value: list):
        self._strong_skills = json.dumps(value or [])

    @property
    def weak_skills(self) -> list:
        try:
            return json.loads(self._weak_skills)
        except Exception:
            return []

    @weak_skills.setter
    def weak_skills(self, value: list):
        self._weak_skills = json.dumps(value or [])

    @property
    def missing_skills(self) -> list:
        try:
            return json.loads(self._missing_skills)
        except Exception:
            return []

    @missing_skills.setter
    def missing_skills(self, value: list):
        self._missing_skills = json.dumps(value or [])

    @property
    def recommendations(self) -> dict:
        try:
            return json.loads(self._recommendations)
        except Exception:
            return {}

    @recommendations.setter
    def recommendations(self, value: dict):
        self._recommendations = json.dumps(value or {})
