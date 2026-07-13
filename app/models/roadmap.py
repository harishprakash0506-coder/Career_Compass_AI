"""
app/models/roadmap.py
─────────────────────
SQLAlchemy ORM model representing historic Learning Roadmap records.
"""

import json
from datetime import datetime
from app.extensions import db


class LearningRoadmap(db.Model):
    """Stores generated 30-60-90 day learning roadmaps for students."""
    
    __tablename__ = 'learning_roadmaps'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    readiness_score_at_generation = db.Column(db.Integer, nullable=False)
    
    # Store 30, 60, 90 day milestones as JSON columns
    _plan_30_day = db.Column('plan_30_day', db.Text, default='[]', nullable=False)
    _plan_60_day = db.Column('plan_60_day', db.Text, default='[]', nullable=False)
    _plan_90_day = db.Column('plan_90_day', db.Text, default='[]', nullable=False)

    # Relationships
    student = db.relationship('StudentProfile', backref=db.backref('roadmaps', cascade='all, delete-orphan'))

    # Getter/setter properties for JSON deserialization
    @property
    def plan_30_day(self) -> list:
        try:
            return json.loads(self._plan_30_day)
        except Exception:
            return []

    @plan_30_day.setter
    def plan_30_day(self, value: list):
        self._plan_30_day = json.dumps(value or [])

    @property
    def plan_60_day(self) -> list:
        try:
            return json.loads(self._plan_60_day)
        except Exception:
            return []

    @plan_60_day.setter
    def plan_60_day(self, value: list):
        self._plan_60_day = json.dumps(value or [])

    @property
    def plan_90_day(self) -> list:
        try:
            return json.loads(self._plan_90_day)
        except Exception:
            return []

    @plan_90_day.setter
    def plan_90_day(self, value: list):
        self._plan_90_day = json.dumps(value or [])
