"""
app/student/routes.py
──────────────────────
Student Portal Blueprint routes for CareerCompass AI.
Handles dashboard, profile management (personal details, skills, projects, internships, certifications),
resume upload page, assessments dashboard, and career readiness scores.
"""

from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app.student import student_bp
from app.extensions import db
from app.models.student import StudentProfile
from app.models.assessment import Assessment
from app.models.placement import PlacementRecord, ResumeAnalysis
from app.utils.decorators import student_required
from app.student.forms import StudentProfileForm, SkillForm, ProjectForm, InternshipForm, CertificationForm


from app.models.progress import StudentProgressLog


@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    """Render the student dashboard home."""
    profile = current_user.student_profile
    if not profile:
        # Auto-create if somehow missing
        profile = StudentProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
    
    # Fetch recent assessments
    assessments = Assessment.query.filter_by(student_id=profile.id).order_by(Assessment.completed_at.desc()).limit(5).all()
    
    # Fetch placement status
    placements = PlacementRecord.query.filter_by(student_id=profile.id).order_by(PlacementRecord.applied_at.desc()).all()
    
    # Fetch resume analysis
    resume_analysis = ResumeAnalysis.query.filter_by(student_id=profile.id).order_by(ResumeAnalysis.analyzed_at.desc()).first()

    # Fetch progress logs for charts
    progress_logs = StudentProgressLog.query.filter_by(student_id=profile.id).order_by(StudentProgressLog.logged_at.asc()).all()
    
    # Compute improvement metrics
    improvement_str = "+0% this month"
    if len(progress_logs) >= 2:
        oldest_score = progress_logs[0].career_readiness_score
        latest_score = progress_logs[-1].career_readiness_score
        diff = latest_score - oldest_score
        sign = "+" if diff >= 0 else ""
        improvement_str = f"{sign}{diff}% overall"

    return render_template(
        'student/dashboard.html',
        profile=profile,
        assessments=assessments,
        placements=placements,
        resume_analysis=resume_analysis,
        progress_logs=progress_logs,
        improvement_str=improvement_str
    )


@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@student_required
def profile():
    """View and update student profile personal and academic details."""
    profile_obj = current_user.student_profile
    if not profile_obj:
        profile_obj = StudentProfile(user_id=current_user.id)
        db.session.add(profile_obj)
        db.session.commit()

    form = StudentProfileForm(obj=profile_obj)
    
    # Instantiate nested sub-item forms
    skill_form = SkillForm()
    project_form = ProjectForm()
    internship_form = InternshipForm()
    cert_form = CertificationForm()

    if form.validate_on_submit() and 'submit' in request.form:
        form.populate_obj(profile_obj)
        profile_obj.compute_profile_completeness()
        db.session.commit()
        flash('Academic and personal profile details updated successfully.', 'success')
        return redirect(url_for('student.profile'))

    return render_template(
        'student/profile.html',
        profile=profile_obj,
        form=form,
        skill_form=skill_form,
        project_form=project_form,
        internship_form=internship_form,
        cert_form=cert_form
    )


# ── Nested items CRUD operations ──────────────────────────────────────────────

@student_bp.route('/profile/skill/add', methods=['POST'])
@login_required
@student_required
def add_skill():
    """Add a skill to the student's dynamic skill list."""
    profile_obj = current_user.student_profile
    form = SkillForm()
    if form.validate_on_submit():
        new_skill = form.skill_name.data.strip()
        current_skills = profile_obj.skills or []
        if new_skill and new_skill not in current_skills:
            current_skills.append(new_skill)
            profile_obj.skills = current_skills
            profile_obj.compute_profile_completeness()
            db.session.commit()
            flash(f'Skill "{new_skill}" added.', 'success')
        else:
            flash('Skill already exists or is invalid.', 'warning')
    return redirect(url_for('student.profile'))


@student_bp.route('/profile/skill/delete/<int:index>', methods=['POST'])
@login_required
@student_required
def delete_skill(index):
    """Delete a skill by index from the student's skill list."""
    profile_obj = current_user.student_profile
    current_skills = profile_obj.skills or []
    if 0 <= index < len(current_skills):
        removed = current_skills.pop(index)
        profile_obj.skills = current_skills
        profile_obj.compute_profile_completeness()
        db.session.commit()
        flash(f'Skill "{removed}" removed.', 'info')
    return redirect(url_for('student.profile'))


@student_bp.route('/profile/project/add', methods=['POST'])
@login_required
@student_required
def add_project():
    """Add a project to the projects JSON array."""
    profile_obj = current_user.student_profile
    form = ProjectForm()
    if form.validate_on_submit():
        tech_list = [t.strip() for t in form.technologies.data.split(',') if t.strip()]
        project = {
            'title': form.title.data.strip(),
            'description': form.description.data.strip(),
            'technologies': tech_list,
            'url': form.url.data.strip() if form.url.data else '',
            'duration': form.duration.data.strip()
        }
        projects = profile_obj.projects or []
        projects.append(project)
        profile_obj.projects = projects
        profile_obj.compute_profile_completeness()
        db.session.commit()
        flash('Project added successfully.', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Project Error: {error}', 'danger')
    return redirect(url_for('student.profile'))


@student_bp.route('/profile/project/delete/<int:index>', methods=['POST'])
@login_required
@student_required
def delete_project(index):
    """Delete a project by index."""
    profile_obj = current_user.student_profile
    projects = profile_obj.projects or []
    if 0 <= index < len(projects):
        removed = projects.pop(index)
        profile_obj.projects = projects
        profile_obj.compute_profile_completeness()
        db.session.commit()
        flash(f'Project "{removed["title"]}" removed.', 'info')
    return redirect(url_for('student.profile'))


@student_bp.route('/profile/internship/add', methods=['POST'])
@login_required
@student_required
def add_internship():
    """Add an internship experience."""
    profile_obj = current_user.student_profile
    form = InternshipForm()
    if form.validate_on_submit():
        internship = {
            'company': form.company.data.strip(),
            'role': form.role.data.strip(),
            'duration': form.duration.data.strip(),
            'description': form.description.data.strip(),
            'stipend': form.stipend.data.strip() if form.stipend.data else ''
        }
        internships = profile_obj.internships or []
        internships.append(internship)
        profile_obj.internships = internships
        profile_obj.compute_profile_completeness()
        db.session.commit()
        flash('Internship record added.', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Internship Error: {error}', 'danger')
    return redirect(url_for('student.profile'))


@student_bp.route('/profile/internship/delete/<int:index>', methods=['POST'])
@login_required
@student_required
def delete_internship(index):
    """Delete internship experience by index."""
    profile_obj = current_user.student_profile
    internships = profile_obj.internships or []
    if 0 <= index < len(internships):
        removed = internships.pop(index)
        profile_obj.internships = internships
        profile_obj.compute_profile_completeness()
        db.session.commit()
        flash(f'Internship at {removed["company"]} removed.', 'info')
    return redirect(url_for('student.profile'))


@student_bp.route('/profile/certification/add', methods=['POST'])
@login_required
@student_required
def add_certification():
    """Add a professional certification."""
    profile_obj = current_user.student_profile
    form = CertificationForm()
    if form.validate_on_submit():
        cert = {
            'name': form.name.data.strip(),
            'issuer': form.issuer.data.strip(),
            'date': form.date.data.strftime('%Y-%m-%d'),
            'credential_url': form.credential_url.data.strip() if form.credential_url.data else ''
        }
        certs = profile_obj.certifications or []
        certs.append(cert)
        profile_obj.certifications = certs
        profile_obj.compute_profile_completeness()
        db.session.commit()
        flash('Certification record added.', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Certification Error: {error}', 'danger')
    return redirect(url_for('student.profile'))


@student_bp.route('/profile/certification/delete/<int:index>', methods=['POST'])
@login_required
@student_required
def delete_certification(index):
    """Delete certification record by index."""
    profile_obj = current_user.student_profile
    certs = profile_obj.certifications or []
    if 0 <= index < len(certs):
        removed = certs.pop(index)
        profile_obj.certifications = certs
        profile_obj.compute_profile_completeness()
        db.session.commit()
        flash(f'Certification "{removed["name"]}" removed.', 'info')
    return redirect(url_for('student.profile'))

