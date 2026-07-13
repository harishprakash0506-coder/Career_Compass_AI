"""
app/models/placement.py
────────────────────────
PlacementRecord  — tracks a student's job application pipeline.
ResumeAnalysis   — stores ATS scoring results for uploaded PDF resumes.
"""

import json
from datetime import datetime
from app.extensions import db


class PlacementRecord(db.Model):
    """
    Tracks each job application a student has made.
    Status lifecycle: applied → shortlisted → interview → selected | rejected
    """

    __tablename__ = 'placement_records'

    STATUSES = ['applied', 'shortlisted', 'interview', 'selected', 'rejected']

    # ── Columns ──────────────────────────────────────────────────────────────────
    id         = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(
        db.Integer,
        db.ForeignKey('student_profiles.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    company_name  = db.Column(db.String(200), nullable=False)
    role          = db.Column(db.String(150))
    package_lpa   = db.Column(db.Float)          # Package in lakhs per annum
    status        = db.Column(db.String(20), nullable=False, default='applied')
    drive_date    = db.Column(db.Date)            # Campus drive date
    notes         = db.Column(db.Text)

    applied_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    @property
    def is_placed(self) -> bool:
        return self.status == 'selected'

    @property
    def status_color(self) -> str:
        """Bootstrap color class for the status badge."""
        mapping = {
            'applied':     'primary',
            'shortlisted': 'info',
            'interview':   'warning',
            'selected':    'success',
            'rejected':    'danger',
        }
        return mapping.get(self.status, 'secondary')

    def __repr__(self) -> str:
        return f'<PlacementRecord student_id={self.student_id} company={self.company_name!r} status={self.status!r}>'


class ResumeAnalysis(db.Model):
    """
    Stores the result of an ATS analysis run on a student's uploaded PDF resume.
    JSON columns hold lists of strings (keywords / feedback items).
    """

    __tablename__ = 'resume_analyses'

    # ── Columns ──────────────────────────────────────────────────────────────────
    id         = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(
        db.Integer,
        db.ForeignKey('student_profiles.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    filename          = db.Column(db.String(250), nullable=False)
    word_count        = db.Column(db.Integer, default=0)

    # ── ATS Score Breakdown (0–100 each) ──────────────────────────────────────
    ats_score         = db.Column(db.Float, nullable=False, default=0.0)   # Overall
    keyword_score     = db.Column(db.Float, nullable=False, default=0.0)   # Keyword match %
    formatting_score  = db.Column(db.Float, nullable=False, default=0.0)   # Structure quality

    # ── JSON-backed Feedback Lists ────────────────────────────────────────────
    _found_keywords      = db.Column('found_keywords',      db.Text, nullable=False, default='[]')
    _missing_keywords    = db.Column('missing_keywords',    db.Text, nullable=False, default='[]')
    _formatting_feedback = db.Column('formatting_feedback', db.Text, nullable=False, default='[]')

    # ── Raw Extracted Text ────────────────────────────────────────────────────
    raw_text = db.Column(db.Text)

    analyzed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # ── JSON Property Accessors ───────────────────────────────────────────────
    @property
    def found_keywords(self) -> list:
        try:
            return json.loads(self._found_keywords) if self._found_keywords else []
        except (json.JSONDecodeError, TypeError):
            return []

    @found_keywords.setter
    def found_keywords(self, value: list) -> None:
        self._found_keywords = json.dumps(value if isinstance(value, list) else [])

    @property
    def missing_keywords(self) -> list:
        try:
            return json.loads(self._missing_keywords) if self._missing_keywords else []
        except (json.JSONDecodeError, TypeError):
            return []

    @missing_keywords.setter
    def missing_keywords(self, value: list) -> None:
        self._missing_keywords = json.dumps(value if isinstance(value, list) else [])

    @property
    def formatting_feedback(self) -> list:
        try:
            return json.loads(self._formatting_feedback) if self._formatting_feedback else []
        except (json.JSONDecodeError, TypeError):
            return []

    @formatting_feedback.setter
    def formatting_feedback(self, value: list) -> None:
        self._formatting_feedback = json.dumps(value if isinstance(value, list) else [])

    @property
    def ats_grade(self) -> str:
        """Letter grade derived from ats_score."""
        score = self.ats_score
        if score >= 85:
            return 'A'
        if score >= 70:
            return 'B'
        if score >= 55:
            return 'C'
        if score >= 40:
            return 'D'
        return 'F'

    def __repr__(self) -> str:
        return f'<ResumeAnalysis student_id={self.student_id} ats={self.ats_score}>'
