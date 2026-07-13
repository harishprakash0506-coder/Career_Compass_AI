"""
app/student/roadmap_routes.py
─────────────────────────────
Student Personalized Learning Roadmap module routes.
Generates and displays 30-60-90 day milestone guides for student preparation.
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.student import student_bp
from app.extensions import db
from app.models.roadmap import LearningRoadmap
from app.utils.decorators import student_required
from app.utils.roadmap_generator import generate_milestone_roadmap


@student_bp.route('/roadmap', methods=['GET'])
@login_required
@student_required
def roadmap():
    """Render the student's personalized learning roadmap page."""
    profile = current_user.student_profile
    
    # Retrieve the latest generated roadmap
    current_roadmap = LearningRoadmap.query.filter_by(student_id=profile.id).order_by(LearningRoadmap.created_at.desc()).first()

    return render_template(
        'student/roadmap.html',
        profile=profile,
        roadmap=current_roadmap
    )


@student_bp.route('/roadmap/generate', methods=['POST'])
@login_required
@student_required
def generate_roadmap():
    """Generate a new learning roadmap based on latest student metrics."""
    profile = current_user.student_profile
    
    # Generate plans
    plans = generate_milestone_roadmap(profile)
    
    # Create database record
    new_roadmap = LearningRoadmap(
        student_id=profile.id,
        readiness_score_at_generation=profile.career_readiness_score or 0,
        plan_30_day=plans["plan_30_day"],
        plan_60_day=plans["plan_60_day"],
        plan_90_day=plans["plan_90_day"]
    )
    db.session.add(new_roadmap)
    db.session.commit()
    
    flash('Personalized learning roadmap generated/updated successfully!', 'success')
    return redirect(url_for('student.roadmap'))
