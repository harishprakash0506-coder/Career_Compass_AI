"""
app/utils/roadmap_generator.py
──────────────────────────────
Generates structured 30-60-90 day learning roadmaps for students based on their
current skill gaps and composite Career Readiness Index.
"""

from typing import Dict, Any, List
from app.models.student import StudentProfile
from app.models.skill_gap import SkillGapAnalysis
from app.utils.skill_gap_calculator import analyze_skill_gap


def generate_milestone_roadmap(profile: StudentProfile) -> Dict[str, List[str]]:
    """
    Produce 30-day, 60-day, and 90-day progress checklist targets based on
    missing/weak skills and the overall Career Readiness index.
    """
    # 1. Fetch current gaps (using default Software Engineer requirements comparison)
    gaps = analyze_skill_gap(profile, "Software Engineer")
    missing = gaps["missing_skills"]
    weak = gaps["weak_skills"]
    
    plan_30 = []
    plan_60 = []
    plan_90 = []
    
    # ── 30-Day Targets: Core Gaps, Academics & Backlogs ──
    if profile.backlogs and profile.backlogs > 0:
        plan_30.append(f"Clear active backlogs: Prioritize exam prep to clear your {profile.backlogs} backlog(s).")
    
    if profile.cgpa and profile.cgpa < 7.0:
        plan_30.append("Improve academic GPA: Dedicated study routines to target 7.0+ CGPA in the next semester.")
        
    # Pick first 2 missing skills to address first
    for i, m_skill in enumerate(missing[:2]):
        plan_30.append(f"Learn foundational concepts of {m_skill}: Study basics and syntax.")
        
    if not plan_30:
        plan_30.append("Consolidate core languages (Python/Java): Focus on advanced class structures.")
        plan_30.append("Practice daily reasoning/logical puzzles to keep your aptitude sharp.")

    # ── 60-Day Targets: Intermediate Skills & Project Builds ──
    # Pick any remaining missing skills
    for m_skill in missing[2:4]:
        plan_60.append(f"Acquire skill {m_skill}: Complete introductory courses and write helper scripts.")
        
    # Address weak skills through project development
    for w_skill in weak[:2]:
        plan_60.append(f"Strengthen {w_skill} through projects: Build a simple web/CLI tool using it.")
        
    if len(profile.projects or []) < 2:
        plan_60.append("Build a portfolio project: Complete at least one web tool or utility app.")
        
    if not plan_60:
        plan_60.append("System Design basics: Study REST APIs, MVC structure, and simple architecture.")
        plan_60.append("Build a full-stack REST API application for your portfolio.")

    # ── 90-Day Targets: Advanced Quizzes, Resume Optimisation & Certifications ──
    # Focus on remaining weak skills and mock assessments
    for w_skill in weak[2:]:
        plan_90.append(f"Master {w_skill}: Take practice tests and attempt complex problem sets.")
        
    for m_skill in missing[:2]:
        plan_90.append(f"Acquire certification for {m_skill}: Prepare for foundational industry exams.")
        
    if profile.career_readiness_score and profile.career_readiness_score < 75:
        plan_90.append("Mock interview runs: Take timed aptitude and technical quizzes weekly.")
        plan_90.append("Resume optimization: Retest your resume on the ATS Analyzer to hit 80+.")
        
    if not plan_90:
        plan_90.append("Conduct mock interview simulations with classmates or placement officers.")
        plan_90.append("Pursue cloud certifications (AWS Practitioner / Azure Fundamentals).")

    return {
        "plan_30_day": plan_30,
        "plan_60_day": plan_60,
        "plan_90_day": plan_90
    }
