"""
app/student/advisor_routes.py
─────────────────────────────
Student AI Career Advisor module routes.
Provides chat interface routing for student questions.
"""

from flask import render_template, request, jsonify
from flask_login import login_required, current_user

from app.student import student_bp
from app.utils.decorators import student_required
from app.utils.advisor_engine import get_advisor_response


@student_bp.route('/advisor', methods=['GET'])
@login_required
@student_required
def advisor():
    """Render the AI Career Advisor chat page."""
    profile = current_user.student_profile
    return render_template('student/advisor.html', profile=profile)


@student_bp.route('/advisor/chat', methods=['POST'])
@login_required
@student_required
def advisor_chat():
    """Process student query and return rule-based advisor response."""
    profile = current_user.student_profile
    data = request.get_json() or {}
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({"response": "Please enter a valid query."})
        
    response_text = get_advisor_response(profile, query)
    return jsonify({"response": response_text})
