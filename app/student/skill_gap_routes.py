"""
app/student/skill_gap_routes.py
───────────────────────────────
Student Skill Gap Analysis module routes.
Compares student skills against target role requirements and stores logs.
"""

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.student import student_bp
from app.extensions import db
from app.models.skill_gap import SkillGapAnalysis
from app.utils.decorators import student_required
from app.utils.skill_gap_calculator import analyze_skill_gap, ROLE_TEMPLATES


@student_bp.route('/skill-gap', methods=['GET', 'POST'])
@login_required
@student_required
def skill_gap():
    """Render the Skill Gap Analysis page, perform comparison checks, and display historic results."""
    profile = current_user.student_profile
    
    # Fetch historical analyses
    history = SkillGapAnalysis.query.filter_by(student_id=profile.id).order_by(SkillGapAnalysis.analyzed_at.desc()).all()
    
    # Selected/latest analysis preview
    selected_id = request.args.get('analysis_id', type=int)
    current_analysis = None
    if selected_id:
        current_analysis = SkillGapAnalysis.query.filter_by(id=selected_id, student_id=profile.id).first()
    if not current_analysis and history:
        current_analysis = history[0]

    # POST: Trigger new analysis
    if request.method == 'POST':
        target_role = request.form.get('target_role', '').strip()
        target_company = request.form.get('target_company', '').strip() or None
        
        if target_role not in ROLE_TEMPLATES:
            flash('Selected target role is invalid.', 'danger')
            return redirect(url_for('student.skill_gap'))
            
        results = analyze_skill_gap(profile, target_role)
        
        # Save to database
        analysis_record = SkillGapAnalysis(
            student_id=profile.id,
            target_role=target_role,
            target_company=target_company,
            strong_skills=results['strong_skills'],
            weak_skills=results['weak_skills'],
            missing_skills=results['missing_skills'],
            recommendations=results['recommendations']
        )
        db.session.add(analysis_record)
        db.session.commit()
        
        flash(f'Skill Gap Analysis for "{target_role}" completed successfully!', 'success')
        return redirect(url_for('student.skill_gap', analysis_id=analysis_record.id))

    return render_template(
        'student/skill_gap.html',
        profile=profile,
        roles=ROLE_TEMPLATES.keys(),
        analysis=current_analysis,
        history=history
    )


@student_bp.route('/skill-gap/delete/<int:analysis_id>', methods=['POST'])
@login_required
@student_required
def delete_skill_gap(analysis_id):
    """Delete a specific skill gap analysis record from history."""
    profile = current_user.student_profile
    record = SkillGapAnalysis.query.filter_by(id=analysis_id, student_id=profile.id).first_or_404()
    
    db.session.delete(record)
    db.session.commit()
    flash('Skill gap history record deleted.', 'info')
    return redirect(url_for('student.skill_gap'))
