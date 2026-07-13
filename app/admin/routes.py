"""
app/admin/routes.py
───────────────────
Admin Control Portal routes for CareerCompass AI.
Provides:
- Dashboard: Platform user accounts overview and system stats.
- User Management: Listing all users and editing account status.
- ML Engine Status: retraining trigger mechanisms.
"""

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.admin import admin_bp
from app.extensions import db
from app.models.user import User, Role
from app.models.student import StudentProfile
from app.models.placement import PlacementRecord
from app.models.assessment import Assessment, Question
from app.utils.decorators import admin_required
from app.ml.train_model import train_placement_model


from sqlalchemy import func
import io
import csv
from flask import make_response
from app.utils.resume_parser import INDUSTRY_KEYWORDS


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Render Admin Dashboard containing platform stats."""
    user_count = User.query.count()
    student_count = StudentProfile.query.count()
    officer_count = User.query.filter_by(role=Role.OFFICER).count()
    
    # Platform activity stats
    total_quizzes = Assessment.query.count()
    total_placements = PlacementRecord.query.count()

    # Calculate average readiness score
    avg_readiness = db.session.query(func.avg(StudentProfile.career_readiness_score)).scalar() or 0.0
    
    # Calculate placement rate
    placed_count = PlacementRecord.query.filter_by(status='selected').distinct(PlacementRecord.student_id).count()
    placement_rate = round((placed_count / student_count) * 100, 1) if student_count > 0 else 0.0

    # Calculate top skill gaps (most frequently missing skills across all students)
    students = StudentProfile.query.all()
    all_target_skills = []
    for kws in INDUSTRY_KEYWORDS.values():
        all_target_skills.extend(kws)

    gap_counts = {skill: 0 for skill in all_target_skills}
    for s in students:
        s_skills = [sk.lower().strip() for sk in (s.skills or [])]
        for skill in all_target_skills:
            if skill.lower() not in s_skills:
                gap_counts[skill] += 1
                
    # Sort and pick top 5 missing skills
    top_gaps = sorted(gap_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_gaps_list = [{"skill": k.title(), "count": v} for k, v in top_gaps]

    return render_template(
        'admin/dashboard.html',
        user_count=user_count,
        student_count=student_count,
        officer_count=officer_count,
        total_quizzes=total_quizzes,
        total_placements=total_placements,
        avg_readiness=round(avg_readiness, 1),
        placement_rate=placement_rate,
        top_gaps=top_gaps_list
    )


@admin_bp.route('/analytics/export', methods=['GET'])
@login_required
@admin_required
def export_analytics():
    """Export system-wide analytics report as CSV."""
    user_count = User.query.count()
    student_count = StudentProfile.query.count()
    officer_count = User.query.filter_by(role=Role.OFFICER).count()
    total_quizzes = Assessment.query.count()
    total_placements = PlacementRecord.query.count()

    avg_readiness = db.session.query(func.avg(StudentProfile.career_readiness_score)).scalar() or 0.0
    placed_count = PlacementRecord.query.filter_by(status='selected').distinct(PlacementRecord.student_id).count()
    placement_rate = round((placed_count / student_count) * 100, 1) if student_count > 0 else 0.0

    si = io.StringIO()
    cw = csv.writer(si)
    
    cw.writerow(['System Analytic Metric', 'Value'])
    cw.writerow(['Total Accounts Registered', user_count])
    cw.writerow(['Student Profiles tracked', student_count])
    cw.writerow(['Placement Officers', officer_count])
    cw.writerow(['Total Quiz Assessments finished', total_quizzes])
    cw.writerow(['Placement Drives Logs entries', total_placements])
    cw.writerow(['Average Readiness Index', round(avg_readiness, 1)])
    cw.writerow(['Overall Placement Rate (%)', placement_rate])
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=System_Analytics_Report.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@admin_bp.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def users():
    """Render all users on the platform and toggle activation status."""
    if request.method == 'POST':
        # Toggle user active status
        user_id = request.form.get('user_id', type=int)
        user_obj = User.query.get_or_404(user_id)
        
        if user_obj.id == 1: # Prevent locking out main admin
            flash('Cannot modify primary administrator account status.', 'warning')
        else:
            user_obj.is_active = not user_obj.is_active
            db.session.commit()
            status = 'activated' if user_obj.is_active else 'deactivated'
            flash(f'Account for {user_obj.full_name} has been {status}.', 'success')
        return redirect(url_for('admin.users'))
        
    user_list = User.query.order_by(User.id.desc()).all()
    return render_template('admin/users.html', users=user_list)


@admin_bp.route('/ml-status', methods=['GET', 'POST'])
@login_required
@admin_required
def ml_status():
    """Monitor Random Forest ML health and trigger retraining."""
    if request.method == 'POST':
        try:
            # Retrain model pickle files
            train_placement_model()
            flash('ML Random Forest Classifier successfully retrained and pickled!', 'success')
        except Exception as e:
            flash(f'Failed to retrain model: {str(e)}', 'danger')
        return redirect(url_for('admin.ml_status'))
        
    return render_template('admin/ml_status.html')
