"""
app/student/resume_forms.py
───────────────────────────
Forms for the ATS Resume Analyzer module.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField


class ResumeUploadForm(FlaskForm):
    """Form to handle PDF resume uploads."""
    
    resume = FileField(
        'Upload Resume (PDF only)',
        validators=[
            FileRequired(message='Please choose a file to upload.'),
            FileAllowed(['pdf'], 'Only PDF files are supported.')
        ]
    )
    submit = SubmitField('Analyze Resume')
