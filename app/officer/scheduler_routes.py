"""
app/officer/scheduler_routes.py
───────────────────────────────
Allows Placement Officers to schedule assessments and export lists.
This extends officer routes in app/officer/routes.py.
"""

import io
import csv
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, Response, make_response
from flask_login import login_required

from app.officer import officer_bp
from app.extensions import db
from app.models.user import User, Role
from app.models.student import StudentProfile
from app.models.assessment import Question
from app.utils.decorators import officer_required


@officer_bp.route('/assessments/schedule', methods=['GET', 'POST'])
@login_required
@officer_required
def schedule_assessments():
    """Allows Placement Officers to view, create, or schedule student quizzes."""
    if request.method == 'POST':
        category = request.form.get('category')
        topic = request.form.get('topic', '').strip()
        text = request.form.get('text', '').strip()
        options_raw = request.form.get('options', '').split(',')
        correct_index = request.form.get('correct_index', type=int)
        difficulty = request.form.get('difficulty', 'medium')

        options = [o.strip() for o in options_raw if o.strip()]

        if category and topic and text and len(options) >= 2 and correct_index is not None:
            # Create a new question in the shared question bank
            q = Question(
                category=category,
                difficulty=difficulty,
                topic=topic,
                text=text,
                correct_index=correct_index
            )
            q.options = options
            db.session.add(q)
            db.session.commit()
            
            flash('Quiz assessment question scheduled/added to repository!', 'success')
        else:
            flash('Error scheduling assessment question. Ensure all fields are filled.', 'danger')
        return redirect(url_for('officer.schedule_assessments'))

    # GET: List active question bank entries
    questions = Question.query.order_by(Question.id.desc()).all()
    return render_template('officer/schedule.html', questions=questions)


@officer_bp.route('/students/export', methods=['GET'])
@login_required
@officer_required
def export_students():
    """Export list of eligible students (CGPA >= 7.0, no backlogs) to CSV."""
    students = StudentProfile.query.filter(
        StudentProfile.cgpa >= 7.0,
        StudentProfile.backlogs == 0
    ).all()

    # Generate CSV in memory
    si = io.StringIO()
    cw = csv.writer(si)
    
    # Header
    cw.writerow(['Ranked Candidate Name', 'Email Address', 'Branch Specialisation', 'CGPA', 'Readiness Score'])
    
    # Content
    for s in students:
        cw.writerow([
            s.user.full_name,
            s.user.email,
            s.branch or 'N/A',
            s.cgpa or 0.0,
            s.career_readiness_score or 0
        ])
        
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=Eligible_Candidates_List.csv"
    output.headers["Content-type"] = "text/csv"
    return output
