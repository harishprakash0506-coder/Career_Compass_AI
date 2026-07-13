"""
app/utils/advisor_engine.py
───────────────────────────
Rule-based Career Advisor Engine that processes student queries
and matches them against profile data, skill gaps, and company match results.
No API key required; relies on pattern-matching rules and student parameters.
"""

from typing import Dict, Any
from app.models.student import StudentProfile
from app.utils.readiness_calculator import calculate_comprehensive_readiness
from app.utils.company_matcher import evaluate_company_matches


def get_advisor_response(profile: StudentProfile, query: str) -> str:
    """
    Generate structured responses using rule-based pattern matching.
    Includes insights from the student's CGPA, backlogs, skills, and match stats.
    """
    q_lower = query.lower()
    
    # 1. Calculate student statistics
    metrics = calculate_comprehensive_readiness(profile)
    company_matches = evaluate_company_matches(profile)
    gpa = profile.cgpa or 0.0
    backlogs = profile.backlogs or 0
    skills = profile.skills or []
    
    # 2. Match patterns in student query
    # TCS match query
    if "tcs" in q_lower or "tata consultancy" in q_lower:
        match_data = next((c for c in company_matches if c["company_name"] == "TCS"), None)
        if match_data:
            eligible_str = "are eligible" if match_data["eligible"] else "are not eligible yet (check your GPA/quizzes)"
            missing = ", ".join(match_data["missing_skills"]) if match_data["missing_skills"] else "None"
            return (
                f"For <b>TCS</b>, you currently have a match score of <b>{match_data['match_percentage']}%</b> and you {eligible_str}.<br/><br/>"
                f"<b>Requirements Checklist:</b><br/>"
                f"• Min CGPA: 6.0 (Your CGPA: {gpa})<br/>"
                f"• Max Backlogs: 2 (Your Backlogs: {backlogs})<br/>"
                f"• Missing Skills: {missing}<br/><br/>"
                f"<b>Improvement Tips:</b><br/>"
                f"TCS values foundational skills. Ensure you add HTML, CSS, SQL, and Python to your profile. "
                f"Keep active backlogs under 2 and maintain your quiz average above 50%."
            )
            
    # Google match query
    elif "google" in q_lower:
        match_data = next((c for c in company_matches if c["company_name"] == "Google"), None)
        if match_data:
            eligible_str = "are eligible" if match_data["eligible"] else "are not eligible (requires 8.0+ CGPA and 75%+ Quiz average)"
            missing = ", ".join(match_data["missing_skills"]) if match_data["missing_skills"] else "None"
            return (
                f"For <b>Google</b>, your match score is <b>{match_data['match_percentage']}%</b>. Currently you {eligible_str}.<br/><br/>"
                f"<b>Key Requirements:</b><br/>"
                f"• Min CGPA: 8.0 (Your CGPA: {gpa})<br/>"
                f"• Missing Skills: {missing}<br/><br/>"
                f"<b>Improvement Tips:</b><br/>"
                f"Google recruitment is heavily focused on Data Structures, Algorithms, and System Design. "
                f"Prioritize practicing coding challenges in our Assessment Engine, improve your resume score to 85+, "
                f"and ensure you have at least 2 major engineering projects listed in your portfolio."
            )

    # General eligibility checks
    elif "eligible" in q_lower or "chance" in q_lower or "probability" in q_lower:
        eligible_count = len([c for c in company_matches if c["eligible"]])
        return (
            f"Based on your <b>Readiness Index of {metrics['career_readiness_score']}/100</b>, "
            f"you are currently eligible for <b>{eligible_count} out of {len(company_matches)}</b> tracked companies.<br/><br/>"
            f"<b>Primary recommendation:</b><br/>"
            f"• Clear any outstanding backlogs (Current: {backlogs})<br/>"
            f"• Maintain a CGPA above 7.5 to open eligibility for Tier-1 companies (Amazon, Microsoft, Google).<br/>"
            f"• Take missing quizzes to raise your Quiz average above 70%."
        )

    # Resume improvements
    elif "resume" in q_lower or "ats" in q_lower:
        return (
            f"Your current Resume ATS compatibility score is <b>{metrics['resume_score']}%</b>.<br/><br/>"
            f"<b>Recommendations:</b><br/>"
            f"1. Navigate to the <b>ATS Resume Analyzer</b> page and upload your latest resume.<br/>"
            f"2. Incorporate matching keywords suggested by our analyzer into your project descriptions.<br/>"
            f"3. Ensure your email, phone, and professional GitHub/LinkedIn URLs are clearly formatted in the header section."
        )

    # Skill additions
    elif "skill" in q_lower or "learn" in q_lower:
        return (
            f"You currently have <b>{len(skills)} skills</b> listed on your profile.<br/><br/>"
            f"<b>Priority recommendations:</b><br/>"
            f"• Open the <b>Skill Gap Analysis</b> page to run a detailed comparison against your target role.<br/>"
            f"• Focus on learning core industry-expected packages like Git, SQL, and at least one backend language (Python/Java).<br/>"
            f"• Complete the recommended certifications listed under your Skill Gap report."
        )

    # Default fallback response
    return (
        "Hello! I am your AI Career Advisor. I can analyze your profile to answer queries like:<br/>"
        "• <i>'How do I improve my chances at TCS/Google?'</i><br/>"
        "• <i>'Am I eligible for placement drives?'</i><br/>"
        "• <i>'How can I improve my resume score?'</i><br/>"
        "• <i>'What skills should I learn?'</i><br/><br/>"
        "Ask me about any specific company or query related to your career readiness stats."
    )
