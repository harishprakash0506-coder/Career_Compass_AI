"""
app/auth/forms.py
──────────────────
WTForms form classes for authentication.

Phase 1: Class definitions with all fields declared so models and
validators are importable across the project. Full rendering and
server-side validation are wired to templates in Phase 2.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import Role


class LoginForm(FlaskForm):
    """Email + password login form."""

    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message='Email is required.'),
            Email(message='Enter a valid email address.'),
        ],
        render_kw={'placeholder': 'you@example.com', 'id': 'login-email'},
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required.'),
        ],
        render_kw={'placeholder': '••••••••', 'id': 'login-password'},
    )
    remember_me = BooleanField('Keep me signed in', default=False)
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """New account registration form."""

    full_name = StringField(
        'Full Name',
        validators=[
            DataRequired(message='Full name is required.'),
            Length(min=2, max=120, message='Name must be between 2 and 120 characters.'),
        ],
        render_kw={'placeholder': 'Jane Doe', 'id': 'reg-full-name'},
    )
    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message='Email is required.'),
            Email(message='Enter a valid email address.'),
            Length(max=120),
        ],
        render_kw={'placeholder': 'you@college.edu', 'id': 'reg-email'},
    )
    role = SelectField(
        'I am a',
        choices=[
            (Role.STUDENT, 'Student'),
            (Role.OFFICER, 'Placement Officer'),
        ],
        validators=[DataRequired()],
        id='reg-role',
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required.'),
            Length(min=8, message='Password must be at least 8 characters.'),
        ],
        render_kw={'placeholder': 'Min. 8 characters', 'id': 'reg-password'},
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message='Please confirm your password.'),
            EqualTo('password', message='Passwords must match.'),
        ],
        render_kw={'placeholder': 'Repeat password', 'id': 'reg-confirm-password'},
    )
    submit = SubmitField('Create Account')

    def validate_email(self, field):
        """Check that the email is not already registered."""
        from app.models.user import User
        if User.query.filter_by(email=field.data.lower().strip()).first():
            raise ValidationError('An account with this email already exists.')
