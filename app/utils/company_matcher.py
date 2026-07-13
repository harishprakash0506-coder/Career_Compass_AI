"""
app/utils/company_matcher.py
────────────────────────────
Evaluates student eligibility and calculates matching scores against
predefined targets for Google, Microsoft, Amazon, Infosys, TCS, etc.
"""

from typing import Dict, Any, List
from app.models.student import StudentProfile
from app.models.assessment import Assessment

COMPANY_REQUIREMENTS = {
    "Google": {
        "min_cgpa": 8.0,
        "max_backlogs": 0,
        "required_skills": ["Python", "Java", "C++", "Algorithms", "Data Structures", "System Design"],
        "min_assessment_score": 75.0,
        "package_lpa": "24 - 45 LPA"
    },
    "Microsoft": {
        "min_cgpa": 8.0,
        "max_backlogs": 0,
        "required_skills": ["C#", "C++", "Java", "Algorithms", "Data Structures", "Cloud Computing"],
        "min_assessment_score": 75.0,
        "package_lpa": "22 - 40 LPA"
    },
    "Amazon": {
        "min_cgpa": 7.5,
        "max_backlogs": 0,
        "required_skills": ["Java", "C++", "Data Structures", "Algorithms", "REST APIs", "SQL"],
        "min_assessment_score": 70.0,
        "package_lpa": "18 - 32 LPA"
    },
    "Infosys": {
        "min_cgpa": 6.0,
        "max_backlogs": 2,
        "required_skills": ["Python", "Java", "SQL", "HTML", "CSS"],
        "min_assessment_score": 50.0,
        "package_lpa": "3.6 - 7.5 LPA"
    },
    "TCS": {
        "min_cgpa": 6.0,
        "max_backlogs": 2,
        "required_skills": ["Python", "Java", "SQL", "HTML", "CSS"],
        "min_assessment_score": 50.0,
        "package_lpa": "3.3 - 7.0 LPA"
    },
    "Accenture": {
        "min_cgpa": 6.5,
        "max_backlogs": 1,
        "required_skills": ["Java", "SQL", "Git", "REST APIs", "HTML", "CSS"],
        "min_assessment_score": 55.0,
        "package_lpa": "4.5 - 9.0 LPA"
    },
    "Wipro": {
        "min_cgpa": 6.0,
        "max_backlogs": 2,
        "required_skills": ["Python", "Java", "SQL", "HTML", "CSS"],
        "min_assessment_score": 50.0,
        "package_lpa": "3.5 - 6.5 LPA"
    },
    "Cognizant": {
        "min_cgpa": 6.2,
        "max_backlogs": 1,
        "required_skills": ["Python", "SQL", "HTML", "CSS", "Git"],
        "min_assessment_score": 52.0,
        "package_lpa": "4.0 - 8.0 LPA"
    },
    "Capgemini": {
        "min_cgpa": 6.3,
        "max_backlogs": 1,
        "required_skills": ["Java", "SQL", "HTML", "CSS", "Git"],
        "min_assessment_score": 53.0,
        "package_lpa": "4.0 - 7.8 LPA"
    },
    "HCL Technologies": {
        "min_cgpa": 6.0,
        "max_backlogs": 2,
        "required_skills": ["Python", "Java", "SQL", "Git"],
        "min_assessment_score": 50.0,
        "package_lpa": "3.5 - 6.8 LPA"
    }
}


def evaluate_company_matches(profile: StudentProfile) -> List[Dict[str, Any]]:
    """Compare student stats against company profiles and compute eligibility status."""
    gpa = profile.cgpa or 0.0
    backlogs = profile.backlogs or 0
    student_skills = [s.lower().strip() for s in (profile.skills or [])]
    
    # Calculate average assessment score
    assessments = Assessment.query.filter_by(student_id=profile.id).all()
    if assessments:
        quiz_avg = sum(a.score_percentage for a in assessments) / len(assessments)
    else:
        quiz_avg = 0.0
        
    match_results = []
    
    for comp_name, reqs in COMPANY_REQUIREMENTS.items():
        # 1. Eligibility Check
        eligible = True
        reasons = []
        
        if gpa < reqs["min_cgpa"]:
            eligible = False
            reasons.append(f"CGPA is below minimum threshold of {reqs['min_cgpa']}.")
        if backlogs > reqs["max_backlogs"]:
            eligible = False
            reasons.append(f"Active backlogs exceed maximum allowed limit of {reqs['max_backlogs']}.")
        if quiz_avg < reqs["min_assessment_score"]:
            eligible = False
            reasons.append(f"Average quiz score ({round(quiz_avg, 1)}%) is below requirement of {reqs['min_assessment_score']}%")
            
        # 2. Skill match calculation
        req_skills = reqs["required_skills"]
        matched_skills = [s for s in req_skills if s.lower().strip() in student_skills]
        missing_skills = [s for s in req_skills if s.lower().strip() not in student_skills]
        
        skill_match_pct = (len(matched_skills) / len(req_skills)) * 100 if req_skills else 0.0
        
        # 3. Overall Match percentage calculation
        gpa_factor = min(100.0, (gpa / reqs["min_cgpa"]) * 100) if reqs["min_cgpa"] > 0 else 100.0
        quiz_factor = min(100.0, (quiz_avg / reqs["min_assessment_score"]) * 100) if reqs["min_assessment_score"] > 0 else 100.0
        
        overall_match = int((gpa_factor * 0.3) + (quiz_factor * 0.3) + (skill_match_pct * 0.4))
        overall_match = max(10, min(99, overall_match))
        
        # Generate suggestions
        suggestions = []
        if not eligible:
            suggestions.extend(reasons)
        if missing_skills:
            suggestions.append(f"Work on acquiring missing skills: {', '.join(missing_skills[:3])}.")
        if quiz_avg < 70.0:
            suggestions.append("Practice more mock technical quizzes to boost your assessment score metrics.")
            
        if not suggestions:
            suggestions.append("Excellent matching metrics! Ready for placement rounds.")

        match_results.append({
            "company_name": comp_name,
            "match_percentage": overall_match,
            "eligible": eligible,
            "missing_skills": missing_skills,
            "suggestions": suggestions,
            "package_lpa": reqs["package_lpa"]
        })
        
    # Sort results with match percentage descending
    match_results.sort(key=lambda x: x["match_percentage"], reverse=True)
    return match_results
