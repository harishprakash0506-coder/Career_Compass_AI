"""
app/auth/routes.py
───────────────────
Phase 2 — Complete authentication route implementations.

Login   : validates credentials, opens session, redirects by role.
Register: validates form, creates User + StudentProfile, redirects to login.
Logout  : clears session, flashes goodbye message.
"""

from urllib.parse import urlparse

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.auth import auth_bp
from app.auth.forms import LoginForm, RegistrationForm
from app.extensions import db
from app.models.user import User, Role
from app.models.student import StudentProfile


# ── Login ──────────────────────────────────────────────────────────────────────

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    GET  — Render the styled login page.
    POST — Validate credentials, open a session, and redirect by role.
         - Unknown email or wrong password → flash danger, re-render form.
         - Deactivated account → flash warning, re-render form.
         - Success → redirect to 'next' param (safe) or role dashboard.
    """
    if current_user.is_authenticated:
        return _redirect_by_role(current_user)

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user  = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid email address or password. Please try again.', 'danger')
            return render_template('auth/login.html', form=form)

        if not user.is_active:
            flash(
                'Your account has been deactivated. '
                'Please contact the administrator.',
                'warning',
            )
            return render_template('auth/login.html', form=form)

        login_user(user, remember=form.remember_me.data)

        # Honour the 'next' redirect parameter but block open-redirect attacks
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = None

        first_name = user.full_name.split()[0]
        flash(f'Welcome back, {first_name}! You are signed in.', 'success')
        return redirect(next_page or _get_dashboard_url(user))

    return render_template('auth/login.html', form=form)


# ── Register ───────────────────────────────────────────────────────────────────

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    GET  — Render the styled registration page.
    POST — Validate form, persist User, auto-create StudentProfile for students,
           then redirect to login with a success flash.
    """
    if current_user.is_authenticated:
        return _redirect_by_role(current_user)

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(
            full_name=form.full_name.data.strip(),
            email=form.email.data.lower().strip(),
            role=form.role.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()          # persist user so user.id is populated

        # Every student account gets an empty profile stub immediately
        if user.role == Role.STUDENT:
            profile = StudentProfile(user_id=user.id)
            profile.compute_profile_completeness()
            db.session.add(profile)

        db.session.commit()

        flash(
            f'Account created for {user.full_name}! '
            'Please sign in to access your dashboard.',
            'success',
        )
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


# ── Logout ─────────────────────────────────────────────────────────────────────

@auth_bp.route('/logout')
@login_required
def logout():
    """End the current user session and redirect to the landing page."""
    first_name = current_user.full_name.split()[0]
    logout_user()
    flash(f'Goodbye, {first_name}! You have been signed out.', 'info')
    return redirect(url_for('index'))


# ── Private Helpers ────────────────────────────────────────────────────────────

def _redirect_by_role(user):
    """Return a redirect Response to the user's role-appropriate dashboard."""
    return redirect(_get_dashboard_url(user))


def _get_dashboard_url(user) -> str:
    """Resolve the url_for() string for a user's primary dashboard endpoint."""
    if user.is_admin:
        return url_for('admin.dashboard')
    if user.is_officer:
        return url_for('officer.dashboard')
    return url_for('student.dashboard')

