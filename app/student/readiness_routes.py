"""
app/student/readiness_routes.py
───────────────────────────────
Student readiness score calculations and predictions mapping.
This extends the routes defined in app/student/routes.py.
"""

from datetime import datetime, date
from flask import render_template
from flask_login import login_required, current_user

from app.student import student_bp
from app.utils.decorators import student_required
from app.utils.readiness_calculator import calculate_comprehensive_readiness
from app.extensions import db
from app.models.progress import StudentProgressLog
from app.models.assessment import Assessment
from app.models.placement import ResumeAnalysis


@student_bp.route('/readiness', methods=['GET'])
@login_required
@student_required
def readiness():
    """Render comprehensive career readiness page with real-time ML predictions."""
    profile = current_user.student_profile
    
    # Calculate composite metrics
    metrics = calculate_comprehensive_readiness(profile)
    
    # Sync calculated composite index to DB profile record
    profile.career_readiness_score = metrics['career_readiness_score']
    
    # Fetch quiz categories scores
    assessments = Assessment.query.filter_by(student_id=profile.id).all()
    apt_score = 0.0
    cod_score = 0.0
    tech_score = 0.0
    for a in assessments:
        if a.category == 'aptitude':
            apt_score = max(apt_score, a.score_percentage)
        elif a.category == 'coding':
            cod_score = max(cod_score, a.score_percentage)
        elif a.category == 'technical':
            tech_score = max(tech_score, a.score_percentage)
            
    # Check if a log entry was already written today
    today = date.today()
    existing_log = StudentProgressLog.query.filter_by(student_id=profile.id).filter(
        db.func.date(StudentProgressLog.logged_at) == today
    ).first()
    
    if not existing_log:
        # Save new milestone log
        log = StudentProgressLog(
            student_id=profile.id,
            career_readiness_score=metrics['career_readiness_score'],
            ats_score=int(metrics['resume_score']),
            aptitude_score=apt_score,
            coding_score=cod_score,
            technical_score=tech_score
        )
        db.session.add(log)
        
    db.session.commit()
    
    return render_template(
        'student/readiness.html',
        profile=profile,
        metrics=metrics
    )
