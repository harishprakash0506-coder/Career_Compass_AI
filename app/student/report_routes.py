"""
app/student/report_routes.py
────────────────────────────
Student PDF report generation routes.
Generates and serves student performance summary sheets.
"""

from flask import send_file, flash, redirect, url_for
from flask_login import login_required, current_user

from app.student import student_bp
from app.utils.decorators import student_required
from app.utils.pdf_generator import generate_student_report_pdf


@student_bp.route('/report/download', methods=['GET'])
@login_required
@student_required
def download_report():
    """Generate and return a downloadable PDF summary report card for the student."""
    profile = current_user.student_profile
    if not profile:
        flash("Student profile details missing.", "warning")
        return redirect(url_for('student.dashboard'))
        
    try:
        # Generate Report bytes
        pdf_buffer = generate_student_report_pdf(profile)
        
        filename = f"CareerCompass_Report_{profile.user.full_name.replace(' ', '_')}.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        print(f"Error during report compilation: {e}")
        flash("Could not generate report. Ensure all profile fields are entered.", "danger")
        return redirect(url_for('student.dashboard'))
