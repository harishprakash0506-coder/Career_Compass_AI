"""
app/student/resume_routes.py
────────────────────────────
Contains route mappings for PDF uploads and ATS scoring analysis.
This extends the routes defined in app/student/routes.py.
"""

import os
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user

from app.student import student_bp
from app.extensions import db
from app.models.placement import ResumeAnalysis
from app.utils.decorators import student_required
from app.utils.helpers import save_uploaded_file
from app.utils.resume_parser import extract_text_from_pdf, analyze_resume_text
from app.student.resume_forms import ResumeUploadForm


@student_bp.route('/resume', methods=['GET', 'POST'])
@login_required
@student_required
def resume():
    """Handle resume PDF uploads and display ATS analyzer results."""
    profile = current_user.student_profile
    
    # Retrieve all historic analyses for this student
    history = ResumeAnalysis.query.filter_by(student_id=profile.id).order_by(ResumeAnalysis.analyzed_at.desc()).all()
    
    form = ResumeUploadForm()
    
    # Selected/latest analysis preview
    selected_id = request.args.get('analysis_id', type=int)
    current_analysis = None
    if selected_id:
        current_analysis = ResumeAnalysis.query.filter_by(id=selected_id, student_id=profile.id).first()
    if not current_analysis and history:
        current_analysis = history[0]

    if form.validate_on_submit():
        # Save file to uploads folder
        filename = save_uploaded_file(form.resume.data, subfolder='resumes')
        if filename:
            # Update profile table filename record
            profile.resume_filename = filename
            profile.resume_uploaded_at = datetime.utcnow()
            
            # Resolve absolute filepath
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'resumes', filename)
            
            # Perform text extraction and parsing
            text = extract_text_from_pdf(filepath)
            results = analyze_resume_text(text)
            
            # Create a database record for historic tracking
            analysis_record = ResumeAnalysis(
                student_id=profile.id,
                filename=filename,
                word_count=results['word_count'],
                ats_score=results['ats_score'],
                keyword_score=results['keyword_score'],
                formatting_score=results['formatting_score'],
                found_keywords=results['found_keywords'],
                missing_keywords=results['missing_keywords'],
                formatting_feedback=results['formatting_feedback'],
                raw_text=text
            )
            db.session.add(analysis_record)
            
            # Recalculate profile completeness and unified career score
            profile.compute_profile_completeness()
            
            db.session.commit()
            
            flash('Resume uploaded and analyzed successfully!', 'success')
            return redirect(url_for('student.resume'))
        else:
            flash('Error uploading file. Please ensure it is a valid PDF.', 'danger')

    return render_template(
        'student/resume.html',
        profile=profile,
        form=form,
        analysis=current_analysis,
        history=history
    )


@student_bp.route('/resume/delete-history/<int:analysis_id>', methods=['POST'])
@login_required
@student_required
def delete_resume_history(analysis_id):
    """Delete a specific resume analysis record from history."""
    profile = current_user.student_profile
    record = ResumeAnalysis.query.filter_by(id=analysis_id, student_id=profile.id).first_or_404()
    
    db.session.delete(record)
    db.session.commit()
    flash('Analysis history record deleted.', 'info')
    return redirect(url_for('student.resume'))
