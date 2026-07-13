"""
app/utils/readiness_calculator.py
─────────────────────────────────
Unified Engine to compute composite Career Readiness Index (0-100)
and generate dynamic strengths, weaknesses, and optimization checklists.
"""

from typing import Dict, List, Any
from app.models.student import StudentProfile
from app.models.assessment import Assessment
from app.models.placement import ResumeAnalysis
from app.ml.predict import predict_placement_probability


def calculate_comprehensive_readiness(profile: StudentProfile) -> Dict[str, Any]:
    """
    Calculate Career Readiness Index using four core pillars:
    1. Academics (30% weight) - GPA & Backlog check
    2. Assessments (30% weight) - Quiz scores average
    3. Resume Profile (20% weight) - ATS Match rating
    4. Profile Completeness (20% weight) - Extra-curricular assets check
    """
    # ── 1. Academics (30%) ──
    gpa = profile.cgpa or 0.0
    backlogs = profile.backlogs or 0
    academic_score = (gpa / 10.0) * 100
    # Apply penalty for active backlogs
    academic_score = max(0.0, academic_score - (backlogs * 15))
    
    # ── 2. Assessments (30%) ──
    assessments = Assessment.query.filter_by(student_id=profile.id).all()
    if assessments:
        quiz_avg = sum(a.score_percentage for a in assessments) / len(assessments)
    else:
        quiz_avg = 0.0
    assessment_score = quiz_avg
    
    # ── 3. Resume / ATS (20%) ──
    latest_resume = ResumeAnalysis.query.filter_by(student_id=profile.id).order_by(ResumeAnalysis.analyzed_at.desc()).first()
    resume_score = latest_resume.ats_score if latest_resume else 0.0
    
    # ── 4. Portfolio / Completeness (20%) ──
    completeness_score = profile.profile_completeness or 0.0
    
    # ── Composite readiness index ──
    composite_index = int(
        (academic_score * 0.3) +
        (assessment_score * 0.3) +
        (resume_score * 0.2) +
        (completeness_score * 0.2)
    )
    composite_index = max(10, min(100, composite_index))
    
    # ── Strengths, Weaknesses, and Action Plan ──
    strengths = []
    weaknesses = []
    recommendations = []
    
    # Academic evaluation
    if gpa >= 8.0:
        strengths.append(f"Strong academic footing with CGPA of {gpa}")
    elif gpa < 7.0:
        weaknesses.append(f"Below average CGPA ({gpa}). Focus on exams.")
        recommendations.append("Target standard eligibility cutoffs (7.0+ CGPA) in next semester exams.")
        
    if backlogs > 0:
        weaknesses.append(f"Has {backlogs} active backlog(s).")
        recommendations.append("Prioritize clearing active backlogs to unlock eligibility for top companies.")
        
    # Assessment evaluation
    if assessment_score >= 75:
        strengths.append("High assessment performance in reasoning and technical tests.")
    elif assessment_score < 50:
        weaknesses.append("Struggling with technical or coding assessments.")
        recommendations.append("Take more mock quizzes in DSA and coding sections to improve score.")
        
    # Resume evaluation
    if resume_score >= 80:
        strengths.append(f"ATS compatible resume layout ({resume_score}% match).")
    else:
        weaknesses.append("Low resume ATS compatibility rating.")
        recommendations.append("Add relevant skills and keywords to your resume to increase ATS compatibility.")
        
    # Portfolio elements
    projects_count = len(profile.projects or [])
    if projects_count >= 2:
        strengths.append("Multiple projects listed in profile portfolio.")
    else:
        weaknesses.append("Limited project portfolio.")
        recommendations.append("Document at least 2 personal or academic projects in your profile details.")
        
    # Fallback recommendations if student is performing well
    if not weaknesses:
        strengths.append("Excellent overall placement preparation!")
        recommendations.append("Keep practicing advanced coding quizzes and mock interview sessions.")
        
    # Real-time Random Forest predictions integration
    prediction = predict_placement_probability(
        cgpa=gpa,
        profile_completeness=int(completeness_score),
        resume_score=int(resume_score),
        quiz_average=float(assessment_score),
        backlogs=backlogs
    )

    return {
        "career_readiness_score": composite_index,
        "academic_score": round(academic_score, 1),
        "assessment_score": round(assessment_score, 1),
        "resume_score": round(resume_score, 1),
        "completeness_score": round(completeness_score, 1),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations,
        "placement_probability": prediction["placement_probability"],
        "confidence_score": prediction["confidence_score"]
    }
