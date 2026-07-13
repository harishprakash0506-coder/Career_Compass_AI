"""
app/models/assessment.py
─────────────────────────
Question  — the question bank seeded into the DB.
Assessment — a completed quiz session record for a student.
"""

import json
from datetime import datetime
from app.extensions import db


class Question(db.Model):
    """
    A single multiple-choice question in the question bank.

    category: 'aptitude' | 'coding' | 'technical'
    difficulty: 'easy' | 'medium' | 'hard'
    options: JSON list of 4 string choices, e.g. ["A", "B", "C", "D"]
    correct_index: 0-based index into options for the correct answer
    """

    __tablename__ = 'questions'

    CATEGORIES   = ['aptitude', 'coding', 'technical']
    DIFFICULTIES = ['easy', 'medium', 'hard']

    # ── Columns ──────────────────────────────────────────────────────────────────
    id            = db.Column(db.Integer, primary_key=True)
    category      = db.Column(db.String(20), nullable=False, index=True)
    difficulty    = db.Column(db.String(10), nullable=False, default='medium')
    topic         = db.Column(db.String(100))              # e.g. "Arrays", "Probability"
    text          = db.Column(db.Text, nullable=False)     # Question stem
    _options      = db.Column('options', db.Text, nullable=False)  # JSON list of 4 strings
    correct_index = db.Column(db.Integer, nullable=False)  # 0-indexed correct answer
    explanation   = db.Column(db.Text)                     # Shown after answering

    is_active     = db.Column(db.Boolean, nullable=False, default=True)
    created_at    = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # ── JSON Property Accessor ────────────────────────────────────────────────────
    @property
    def options(self) -> list:
        try:
            return json.loads(self._options) if self._options else []
        except (json.JSONDecodeError, TypeError):
            return []

    @options.setter
    def options(self, value: list) -> None:
        if not isinstance(value, list) or len(value) != 4:
            raise ValueError('A question must have exactly 4 options.')
        self._options = json.dumps(value)

    @property
    def correct_answer(self) -> str:
        """Return the text of the correct answer option."""
        opts = self.options
        if 0 <= self.correct_index < len(opts):
            return opts[self.correct_index]
        return ''

    def __repr__(self) -> str:
        return f'<Question id={self.id} category={self.category!r} difficulty={self.difficulty!r}>'


class Assessment(db.Model):
    """
    Records a single completed quiz session for a student.

    Each session belongs to one category (aptitude / coding / technical).
    Scores are stored as raw counts and a percentage for easy aggregation.
    """

    __tablename__ = 'assessments'

    # ── Columns ──────────────────────────────────────────────────────────────────
    id         = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(
        db.Integer,
        db.ForeignKey('student_profiles.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    category         = db.Column(db.String(20), nullable=False)   # aptitude | coding | technical
    total_questions  = db.Column(db.Integer, nullable=False)
    correct_answers  = db.Column(db.Integer, nullable=False, default=0)
    score_percentage = db.Column(db.Float,   nullable=False, default=0.0)
    duration_seconds = db.Column(db.Integer)                       # Time taken

    # ── Answer Log (JSON: [{question_id, chosen_index, is_correct}, ...]) ──────
    _answer_log = db.Column('answer_log', db.Text, nullable=False, default='[]')

    started_at   = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    # ── Computed Properties ───────────────────────────────────────────────────────
    @property
    def incorrect_answers(self) -> int:
        return self.total_questions - self.correct_answers

    @property
    def is_completed(self) -> bool:
        return self.completed_at is not None

    @property
    def grade(self) -> str:
        """Letter grade derived from score_percentage."""
        pct = self.score_percentage
        if pct >= 85:
            return 'A'
        if pct >= 70:
            return 'B'
        if pct >= 55:
            return 'C'
        if pct >= 40:
            return 'D'
        return 'F'

    @property
    def grade_color(self) -> str:
        """Bootstrap color class for the grade badge."""
        mapping = {'A': 'success', 'B': 'info', 'C': 'warning', 'D': 'warning', 'F': 'danger'}
        return mapping.get(self.grade, 'secondary')

    # ── Answer Log Accessor ───────────────────────────────────────────────────────
    @property
    def answer_log(self) -> list:
        try:
            return json.loads(self._answer_log) if self._answer_log else []
        except (json.JSONDecodeError, TypeError):
            return []

    @answer_log.setter
    def answer_log(self, value: list) -> None:
        self._answer_log = json.dumps(value if isinstance(value, list) else [])

    def compute_score(self) -> float:
        """Recalculate score_percentage from the answer log and persist it."""
        log = self.answer_log
        if not log:
            self.score_percentage = 0.0
            return 0.0
        correct = sum(1 for entry in log if entry.get('is_correct', False))
        self.correct_answers = correct
        pct = round((correct / len(log)) * 100, 2)
        self.score_percentage = pct
        return pct

    def __repr__(self) -> str:
        return (
            f'<Assessment id={self.id} student_id={self.student_id} '
            f'category={self.category!r} score={self.score_percentage}%>'
        )
