"""
app/models/__init__.py
──────────────────────
Imports all ORM models so SQLAlchemy's mapper registers every table
before db.create_all() is called in the application factory.
"""

from app.models.user import User
from app.models.student import StudentProfile
from app.models.placement import PlacementRecord, ResumeAnalysis
from app.models.assessment import Question, Assessment
from app.models.skill_gap import SkillGapAnalysis
from app.models.roadmap import LearningRoadmap
from app.models.progress import StudentProgressLog

__all__ = [
    'User',
    'StudentProfile',
    'PlacementRecord',
    'ResumeAnalysis',
    'Question',
    'Assessment',
    'SkillGapAnalysis',
    'LearningRoadmap',
    'StudentProgressLog',
]
