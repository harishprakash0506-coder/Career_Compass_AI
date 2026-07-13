"""
app/student/company_routes.py
─────────────────────────────
Student Company Match Engine module routes.
Compares student academic stats, assessment scores, and skills against top employers.
"""

from flask import render_template
from flask_login import login_required, current_user

from app.student import student_bp
from app.utils.decorators import student_required
from app.utils.company_matcher import evaluate_company_matches


@student_bp.route('/company-match', methods=['GET'])
@login_required
@student_required
def company_match():
    """Render the Company Matching dashboard."""
    profile = current_user.student_profile
    matches = evaluate_company_matches(profile)
    
    return render_template(
        'student/company_match.html',
        profile=profile,
        matches=matches
    )
