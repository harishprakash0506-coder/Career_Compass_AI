"""
app/models/student.py
──────────────────────
StudentProfile model — stores all academic, personal, and career-related
data for a student user. JSON columns are exposed via Python properties
for clean list access.
"""

import json
from datetime import datetime
from app.extensions import db


class StudentProfile(db.Model):
    """
    One-to-one extension of the User model for role=student.

    JSON-backed columns (skills, projects, internships, certifications)
    are accessed via @property getters/setters that handle serialisation
    transparently, so all calling code works with plain Python lists/dicts.
    """

    __tablename__ = 'student_profiles'

    # ── Primary Key & FK ─────────────────────────────────────────────────────────
    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        unique=True,
        nullable=False,
        index=True,
    )

    # ── Personal Details ─────────────────────────────────────────────────────────
    phone        = db.Column(db.String(15))
    date_of_birth = db.Column(db.Date)
    gender       = db.Column(db.String(20))
    address      = db.Column(db.Text)

    # ── Academic Details ─────────────────────────────────────────────────────────
    college_name       = db.Column(db.String(250))
    branch             = db.Column(db.String(100))    # e.g. "Computer Science"
    specialization     = db.Column(db.String(100))
    year_of_study      = db.Column(db.Integer)        # 1–4
    graduation_year    = db.Column(db.Integer)        # e.g. 2025
    cgpa               = db.Column(db.Float)          # 0.0 – 10.0
    backlogs           = db.Column(db.Integer, default=0)
    tenth_percentage   = db.Column(db.Float)
    twelfth_percentage = db.Column(db.Float)

    # ── JSON-backed Lists ────────────────────────────────────────────────────────
    # skills        : ["Python", "Machine Learning", ...]
    # projects      : [{title, description, technologies, url, duration}, ...]
    # internships   : [{company, role, duration, description, stipend}, ...]
    # certifications: [{name, issuer, date, credential_url}, ...]
    _skills         = db.Column('skills',         db.Text, nullable=False, default='[]')
    _projects       = db.Column('projects',       db.Text, nullable=False, default='[]')
    _internships    = db.Column('internships',    db.Text, nullable=False, default='[]')
    _certifications = db.Column('certifications', db.Text, nullable=False, default='[]')

    # ── External Links ───────────────────────────────────────────────────────────
    linkedin_url  = db.Column(db.String(250))
    github_url    = db.Column(db.String(250))
    portfolio_url = db.Column(db.String(250))

    # ── Resume ───────────────────────────────────────────────────────────────────
    resume_filename    = db.Column(db.String(250))
    resume_uploaded_at = db.Column(db.DateTime)

    # ── Computed / ML Scores (written by scoring & ML modules) ──────────────────
    profile_completeness   = db.Column(db.Float, nullable=False, default=0.0)
    career_readiness_score = db.Column(db.Float, nullable=False, default=0.0)
    placement_probability  = db.Column(db.Float, nullable=False, default=0.0)
    # Tier: Unrated | Developing | Ready | Exceptional
    readiness_tier         = db.Column(db.String(20), nullable=False, default='Unrated')

    # ── Timestamps ───────────────────────────────────────────────────────────────
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # ── Relationships ─────────────────────────────────────────────────────────────
    resume_analyses  = db.relationship(
        'ResumeAnalysis',
        backref='student',
        cascade='all, delete-orphan',
        lazy='dynamic',
        order_by='ResumeAnalysis.analyzed_at.desc()',
    )
    assessments = db.relationship(
        'Assessment',
        backref='student',
        cascade='all, delete-orphan',
        lazy='dynamic',
        order_by='Assessment.completed_at.desc()',
    )
    placement_records = db.relationship(
        'PlacementRecord',
        backref='student',
        cascade='all, delete-orphan',
        lazy='dynamic',
        order_by='PlacementRecord.applied_at.desc()',
    )

    # ── JSON Property Accessors ───────────────────────────────────────────────────
    @property
    def skills(self) -> list:
        try:
            return json.loads(self._skills) if self._skills else []
        except (json.JSONDecodeError, TypeError):
            return []

    @skills.setter
    def skills(self, value: list) -> None:
        self._skills = json.dumps(value if isinstance(value, list) else [])

    @property
    def projects(self) -> list:
        try:
            return json.loads(self._projects) if self._projects else []
        except (json.JSONDecodeError, TypeError):
            return []

    @projects.setter
    def projects(self, value: list) -> None:
        self._projects = json.dumps(value if isinstance(value, list) else [])

    @property
    def internships(self) -> list:
        try:
            return json.loads(self._internships) if self._internships else []
        except (json.JSONDecodeError, TypeError):
            return []

    @internships.setter
    def internships(self, value: list) -> None:
        self._internships = json.dumps(value if isinstance(value, list) else [])

    @property
    def certifications(self) -> list:
        try:
            return json.loads(self._certifications) if self._certifications else []
        except (json.JSONDecodeError, TypeError):
            return []

    @certifications.setter
    def certifications(self, value: list) -> None:
        self._certifications = json.dumps(value if isinstance(value, list) else [])

    # ── Domain Logic ──────────────────────────────────────────────────────────────
    def compute_profile_completeness(self) -> float:
        """
        Calculate and persist profile completeness as a percentage (0–100).
        Weights each field equally across 12 criteria.
        Called whenever the profile is saved/updated.
        """
        criteria = {
            'phone':            bool(self.phone),
            'date_of_birth':    bool(self.date_of_birth),
            'college_name':     bool(self.college_name),
            'branch':           bool(self.branch),
            'year_of_study':    self.year_of_study is not None,
            'cgpa':             self.cgpa is not None,
            'graduation_year':  bool(self.graduation_year),
            'skills':           len(self.skills) >= 3,
            'projects':         len(self.projects) >= 1,
            'internships':      len(self.internships) >= 1,
            'linkedin_url':     bool(self.linkedin_url),
            'resume_filename':  bool(self.resume_filename),
        }
        filled = sum(1 for v in criteria.values() if v)
        self.profile_completeness = round((filled / len(criteria)) * 100, 2)
        return self.profile_completeness

    def get_readiness_tier(self) -> str:
        """Return a human-readable readiness tier based on career_readiness_score."""
        score = self.career_readiness_score
        if score >= 80:
            return 'Exceptional'
        if score >= 60:
            return 'Ready'
        if score >= 35:
            return 'Developing'
        return 'Unrated'

    def __repr__(self) -> str:
        return f'<StudentProfile user_id={self.user_id} cgpa={self.cgpa}>'
