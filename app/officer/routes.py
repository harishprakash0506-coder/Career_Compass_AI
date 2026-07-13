"""
app/officer/routes.py
─────────────────────
Placement Officer portal routes for CareerCompass AI.
Provides:
- Dashboard: Batch placement statistics and metrics.
- Students List: Cohort details, CGPA, and readiness rankings.
- Placement Drives: Student application statuses and package distribution.
"""

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func

from app.officer import officer_bp
from app.extensions import db
from app.models.user import User, Role
from app.models.student import StudentProfile
from app.models.placement import PlacementRecord, ResumeAnalysis
from app.models.assessment import Assessment
from app.utils.decorators import officer_required


@officer_bp.route('/dashboard')
@login_required
@officer_required
def dashboard():
    """Render Placement Officer Dashboard containing cohort analytics."""
    # 1. Basic Stats
    total_students = StudentProfile.query.count()
    placed_students = PlacementRecord.query.filter_by(status='selected').distinct(PlacementRecord.student_id).count()
    placement_rate = round((placed_students / total_students) * 100, 1) if total_students > 0 else 0.0
    
    # 2. Average readiness score
    avg_readiness = db.session.query(func.avg(StudentProfile.career_readiness_score)).scalar() or 0.0
    
    # 3. Average CGPA
    avg_cgpa = db.session.query(func.avg(StudentProfile.cgpa)).scalar() or 0.0
    
    # 4. Top packages (LPA)
    top_package = db.session.query(func.max(PlacementRecord.package_lpa)).scalar() or 0.0
    
    # 5. Cohort Branch Distribution (Count of students in each branch)
    branch_counts = db.session.query(
        StudentProfile.branch, func.count(StudentProfile.id)
    ).group_by(StudentProfile.branch).all()
    
    branch_distribution = {b: count for b, count in branch_counts if b}
    
    return render_template(
        'officer/dashboard.html',
        total_students=total_students,
        placed_students=placed_students,
        placement_rate=placement_rate,
        avg_readiness=round(avg_readiness, 1),
        avg_cgpa=round(avg_cgpa, 2),
        top_package=top_package,
        branch_distribution=branch_distribution
    )


@officer_bp.route('/students')
@login_required
@officer_required
def students():
    """Render students list with search, filter, and readiness rankings."""
    search_query = request.args.get('search', '')
    branch_filter = request.args.get('branch', '')
    
    query = StudentProfile.query.join(User)
    
    if search_query:
        query = query.filter(User.full_name.ilike(f'%{search_query}%'))
    if branch_filter:
        query = query.filter(StudentProfile.branch == branch_filter)
        
    students_list = query.order_by(StudentProfile.career_readiness_score.desc()).all()
    
    # Get distinct branches for filter dropdown
    branches = db.session.query(StudentProfile.branch).distinct().all()
    branches = [b[0] for b in branches if b[0]]

    return render_template(
        'officer/students.html',
        students=students_list,
        branches=branches,
        search_query=search_query,
        branch_filter=branch_filter
    )


@officer_bp.route('/placements', methods=['GET', 'POST'])
@login_required
@officer_required
def placements():
    """Render placement records and manage application tracking."""
    if request.method == 'POST':
        # Add new placement record entry
        student_id = request.form.get('student_id', type=int)
        company = request.form.get('company_name', '').strip()
        role = request.form.get('role', '').strip()
        status = request.form.get('status', 'applied')
        package = request.form.get('package_lpa', type=float)
        
        if student_id and company and role:
            record = PlacementRecord(
                student_id=student_id,
                company_name=company,
                role=role,
                status=status,
                package_lpa=package if status == 'selected' else None
            )
            db.session.add(record)
            db.session.commit()
            flash('Placement record logged successfully!', 'success')
        else:
            flash('Failed to log placement record. Ensure all fields are filled.', 'danger')
        return redirect(url_for('officer.placements'))

    # GET: fetch drive applications list
    records = PlacementRecord.query.order_by(PlacementRecord.applied_at.desc()).all()
    
    # Retrieve all student profiles for selection dropdown
    students_list = StudentProfile.query.join(User).order_by(User.full_name).all()
    
    return render_template(
        'officer/placements.html',
        records=records,
        students=students_list
    )
