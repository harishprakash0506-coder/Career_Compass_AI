"""
app/api/routes.py
──────────────────
REST API blueprint — JSON endpoints consumed by Chart.js and AJAX calls.

Phase 1: /api/health endpoint live. All chart-data and ML-prediction
endpoints are registered and return placeholder-free JSON shapes;
data is populated in Phases 6–8.
"""

from datetime import datetime
from flask import jsonify
from flask_login import login_required, current_user
from app.api import api_bp


@api_bp.route('/health', methods=['GET'])
def health():
    """
    Public health-check endpoint.
    Returns 200 OK when the application is running correctly.
    """
    return jsonify({
        'status': 'ok',
        'app': 'CareerCompass AI',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
    }), 200


@api_bp.route('/dashboard/student', methods=['GET'])
@login_required
def student_dashboard_data():
    """
    Returns Chart.js-ready JSON for the student dashboard.
    Scores and history populated in Phase 8.
    """
    from app.models.student import StudentProfile
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({'error': 'Profile not found.'}), 404

    return jsonify({
        'career_readiness_score': profile.career_readiness_score,
        'placement_probability':  profile.placement_probability,
        'profile_completeness':   profile.profile_completeness,
        'readiness_tier':         profile.readiness_tier,
    }), 200


@api_bp.route('/dashboard/officer', methods=['GET'])
@login_required
def officer_dashboard_data():
    """
    Cohort-level statistics for the Placement Officer dashboard.
    Aggregation logic added in Phase 8.
    """
    from app.models.student import StudentProfile
    from app.models.placement import PlacementRecord

    total_students  = StudentProfile.query.count()
    total_placed    = PlacementRecord.query.filter_by(status='selected').count()
    placement_rate  = round((total_placed / total_students * 100), 2) if total_students else 0.0

    return jsonify({
        'total_students':  total_students,
        'total_placed':    total_placed,
        'placement_rate':  placement_rate,
    }), 200


@api_bp.route('/predict', methods=['POST'])
@login_required
def predict_placement():
    """
    Accepts student feature JSON, returns ML placement prediction.
    ML model integration added in Phase 6.
    """
    return jsonify({
        'message': 'ML engine will be connected in Phase 6.',
        'placement_probability': None,
        'confidence_score': None,
    }), 200
