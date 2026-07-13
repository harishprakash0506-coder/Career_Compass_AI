"""
app/student/forms.py
────────────────────
Forms for the Student Profile and Dashboard modules.
Includes:
- StudentProfileForm: Personal & Academic details
- SkillForm: Managing individual skills
- ProjectForm: Adding/Editing projects
- InternshipForm: Adding/Editing internships
- CertificationForm: Adding/Editing certifications
"""

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, DateField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length, URL


class StudentProfileForm(FlaskForm):
    """Form to edit core personal and academic profile details."""
    
    phone = StringField(
        'Phone Number',
        validators=[
            DataRequired(message='Phone number is required.'),
            Length(min=10, max=15, message='Phone number must be between 10 and 15 digits.')
        ]
    )
    date_of_birth = DateField(
        'Date of Birth',
        format='%Y-%m-%d',
        validators=[DataRequired(message='Date of birth is required.')]
    )
    gender = SelectField(
        'Gender',
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        validators=[DataRequired(message='Please select your gender.')]
    )
    college_name = StringField(
        'College Name',
        validators=[
            DataRequired(message='College name is required.'),
            Length(max=200)
        ]
    )
    branch = SelectField(
        'Branch / Specialisation',
        choices=[
            ('Computer Science & Engineering', 'Computer Science & Engineering'),
            ('Information Technology', 'Information Technology'),
            ('Electronics & Communication Engineering', 'Electronics & Communication Engineering'),
            ('Mechanical Engineering', 'Mechanical Engineering'),
            ('Civil Engineering', 'Civil Engineering'),
            ('Electrical Engineering', 'Electrical Engineering'),
        ],
        validators=[DataRequired(message='Please select your academic branch.')]
    )
    year_of_study = IntegerField(
        'Current Year of Study',
        validators=[
            DataRequired(message='Year of study is required.'),
            NumberRange(min=1, max=5, message='Year must be between 1 and 5.')
        ]
    )
    graduation_year = IntegerField(
        'Graduation Year',
        validators=[
            DataRequired(message='Graduation year is required.'),
            NumberRange(min=2020, max=2035)
        ]
    )
    cgpa = FloatField(
        'CGPA',
        validators=[
            DataRequired(message='CGPA is required.'),
            NumberRange(min=0.0, max=10.0, message='CGPA must be between 0.0 and 10.0.')
        ]
    )
    backlogs = IntegerField(
        'Active Backlogs',
        validators=[
            NumberRange(min=0, max=10, message='Backlogs must be 0 or greater.')
        ],
        default=0
    )
    tenth_percentage = FloatField(
        '10th Grade Percentage',
        validators=[
            DataRequired(message='10th percentage is required.'),
            NumberRange(min=0.0, max=100.0, message='Percentage must be between 0.0 and 100.0.')
        ]
    )
    twelfth_percentage = FloatField(
        '12th Grade / Diploma Percentage',
        validators=[
            DataRequired(message='12th percentage is required.'),
            NumberRange(min=0.0, max=100.0, message='Percentage must be between 0.0 and 100.0.')
        ]
    )
    linkedin_url = StringField(
        'LinkedIn Profile URL',
        validators=[Optional(), URL(message='Enter a valid URL.')]
    )
    github_url = StringField(
        'GitHub Profile URL',
        validators=[Optional(), URL(message='Enter a valid URL.')]
    )
    submit = SubmitField('Save Profile Details')


class SkillForm(FlaskForm):
    """Form to add a single skill."""
    skill_name = StringField(
        'Skill Name',
        validators=[
            DataRequired(message='Skill name cannot be empty.'),
            Length(max=50)
        ]
    )
    submit = SubmitField('Add Skill')


class ProjectForm(FlaskForm):
    """Form to add or edit a project."""
    title = StringField(
        'Project Title',
        validators=[DataRequired(message='Project title is required.'), Length(max=100)]
    )
    description = TextAreaField(
        'Project Description',
        validators=[DataRequired(message='Description is required.'), Length(max=500)]
    )
    technologies = StringField(
        'Technologies Used (comma separated)',
        validators=[DataRequired(message='Provide at least one technology.')]
    )
    url = StringField(
        'Project URL (GitHub / Demo)',
        validators=[Optional(), URL(message='Enter a valid URL.')]
    )
    duration = StringField(
        'Duration (e.g. 3 months)',
        validators=[DataRequired(message='Duration is required.'), Length(max=50)]
    )
    submit = SubmitField('Save Project')


class InternshipForm(FlaskForm):
    """Form to add or edit an internship."""
    company = StringField(
        'Company Name',
        validators=[DataRequired(message='Company name is required.'), Length(max=100)]
    )
    role = StringField(
        'Internship Role',
        validators=[DataRequired(message='Internship role is required.'), Length(max=100)]
    )
    duration = StringField(
        'Duration',
        validators=[DataRequired(message='Duration is required.'), Length(max=50)]
    )
    description = TextAreaField(
        'Job Description',
        validators=[DataRequired(message='Description is required.'), Length(max=500)]
    )
    stipend = StringField(
        'Stipend (optional)',
        validators=[Optional(), Length(max=50)]
    )
    submit = SubmitField('Save Internship')


class CertificationForm(FlaskForm):
    """Form to add or edit a professional certification."""
    name = StringField(
        'Certification Name',
        validators=[DataRequired(message='Certification name is required.'), Length(max=150)]
    )
    issuer = StringField(
        'Issuing Organisation',
        validators=[DataRequired(message='Issuer is required.'), Length(max=100)]
    )
    date = DateField(
        'Date Earned',
        format='%Y-%m-%d',
        validators=[DataRequired(message='Earned date is required.')]
    )
    credential_url = StringField(
        'Credential Verification URL',
        validators=[Optional(), URL(message='Enter a valid URL.')]
    )
    submit = SubmitField('Save Certification')
