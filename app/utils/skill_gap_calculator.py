"""
app/utils/skill_gap_calculator.py
─────────────────────────────────
Calculates skill gaps comparing student's profile skills + assessment scores
against predefined target role templates, generating courses, projects, and certifications recommendations.
"""

from typing import Dict, Any, List
from app.models.student import StudentProfile
from app.models.assessment import Assessment

# Target Role Requirements & Recommendation Templates
ROLE_TEMPLATES = {
    "Software Engineer": {
        "required_skills": ["Python", "Java", "Data Structures", "Algorithms", "SQL", "Git", "OOP"],
        "recommendations": {
            "Python": {
                "course": "Python for Everybody Specialization (Coursera)",
                "project": "Build an Automated File Parser or Web Scraper",
                "cert": "Python Institute Certified Associate (PCAP)"
            },
            "Java": {
                "course": "Java Programming and Software Engineering Fundamentals (Coursera)",
                "project": "Build a CLI Student Management System in Java",
                "cert": "Oracle Certified Associate Java Programmer"
            },
            "Data Structures": {
                "course": "Data Structures and Algorithms Specialization (Coursera / UC San Diego)",
                "project": "Implement Custom Trees and Graph Traversals in Python/Java",
                "cert": "GeeksforGeeks DSA Certification"
            },
            "Algorithms": {
                "course": "Algorithms, Part I & II (Princeton / Coursera)",
                "project": "Build a Pathfinding Visualizer (Dijkstra/A* Search)",
                "cert": "HackerRank Problem Solving Badge"
            },
            "SQL": {
                "course": "Introduction to Databases and SQL (Coursera / Meta)",
                "project": "Design and Normalize a Schema for a Retail Platform",
                "cert": "Oracle Database SQL Certified Associate"
            },
            "Git": {
                "course": "Version Control with Git (Udacity)",
                "project": "Configure a repository with branch protection rules and GitHub Actions CI/CD",
                "cert": "GitHub Actions Certification"
            },
            "OOP": {
                "course": "Object Oriented Programming in Java (Coursera)",
                "project": "Design a simulator application demonstrating Inheritance, Polymorphism, and Encapsulation",
                "cert": "Software Design & OOP Patterns Certificate"
            }
        }
    },
    "Data Scientist": {
        "required_skills": ["Python", "SQL", "Machine Learning", "Deep Learning", "Pandas", "NumPy"],
        "recommendations": {
            "Python": {
                "course": "Google IT Automation with Python Professional Certificate",
                "project": "Write custom scripts to clean and parse dirty CSV datasets",
                "cert": "Microsoft Certified: Power Platform Functional Consultant"
            },
            "SQL": {
                "course": "SQL for Data Science (UC Davis / Coursera)",
                "project": "Analyze E-commerce user behavior patterns using recursive SQL queries",
                "cert": "PostgreSQL 12 Associate Certification"
            },
            "Machine Learning": {
                "course": "Machine Learning Specialization by Andrew Ng (DeepLearning.AI)",
                "project": "Train and optimize a Random Forest model on Kaggle housing datasets",
                "cert": "TensorFlow Developer Certificate"
            },
            "Deep Learning": {
                "course": "Deep Learning Specialization (DeepLearning.AI)",
                "project": "Build a Convolutional Neural Network (CNN) for Image Classification",
                "cert": "AWS Certified Machine Learning - Specialty"
            },
            "Pandas": {
                "course": "Data Analysis with Python (freeCodeCamp)",
                "project": "Exploratory Data Analysis (EDA) on global climate change metrics datasets",
                "cert": "Kaggle Data Cleaning & Visualization Certificates"
            },
            "NumPy": {
                "course": "Scientific Computing with Python (freeCodeCamp)",
                "project": "Implement multi-dimensional matrix operations and linear regression from scratch",
                "cert": "NumPy Fundamentals Certification"
            }
        }
    },
    "Frontend Developer": {
        "required_skills": ["JavaScript", "HTML", "CSS", "React", "Git"],
        "recommendations": {
            "JavaScript": {
                "course": "JavaScript: The Advanced Concepts (Udemy)",
                "project": "Build a Single Page Application (SPA) using vanilla JavaScript DOM Manipulation",
                "cert": "W3Schools JavaScript Developer Certification"
            },
            "HTML": {
                "course": "HTML5 and CSS3 Fundamentals (W3C)",
                "project": "Create a fully accessible, semantic website template matching WCAG 2.1 rules",
                "cert": "Responsive Web Design Certification (freeCodeCamp)"
            },
            "CSS": {
                "course": "CSS - The Complete Guide (Academind / Udemy)",
                "project": "Design a responsive CSS Grid & Flexbox portfolio dashboard layout with glassmorphism styling",
                "cert": "Responsive Web Design Certification (freeCodeCamp)"
            },
            "React": {
                "course": "React - The Complete Guide (Maximilian Schwarzmüller)",
                "project": "Build a movie dashboard consuming public REST APIs with React hooks & context API",
                "cert": "Meta Front-End Developer Professional Certificate"
            },
            "Git": {
                "course": "Git & GitHub Complete Guide (Udemy)",
                "project": "Configure a repository and resolve simulated merge conflicts with teammates",
                "cert": "Atlassian Git Fundamentals Certificate"
            }
        }
    }
}


def analyze_skill_gap(profile: StudentProfile, target_role: str) -> Dict[str, Any]:
    """
    Compare student skills and quiz performance against the target role requirements.
    
    Categorisation:
    - Strong: Skill is in profile AND student has high technical/coding scores (>= 70%) if tested.
    - Weak: Skill is in profile BUT latest quiz score for that domain (e.g. coding/technical) is < 70%.
    - Missing: Skill is not in the student's profile skill list.
    """
    template = ROLE_TEMPLATES.get(target_role)
    if not template:
        # Default fallback template
        template = {
            "required_skills": ["Python", "SQL", "Git"],
            "recommendations": {
                "Python": {"course": "Python Basics", "project": "CLI App", "cert": "Python Cert"},
                "SQL": {"course": "SQL Basics", "project": "DB Schema", "cert": "SQL Cert"},
                "Git": {"course": "Git Basics", "project": "Repo setup", "cert": "Git Cert"}
            }
        }
        
    required_skills = template["required_skills"]
    recommendations_db = template["recommendations"]
    
    # Retrieve student's skills
    student_skills = [s.lower().strip() for s in (profile.skills or [])]
    
    # Get quiz scores to check if present skills are "Weak"
    assessments = Assessment.query.filter_by(student_id=profile.id).all()
    technical_score = 0.0
    coding_score = 0.0
    
    for a in assessments:
        if a.category == 'technical':
            technical_score = max(technical_score, a.score_percentage)
        elif a.category == 'coding':
            coding_score = max(coding_score, a.score_percentage)
            
    strong_skills = []
    weak_skills = []
    missing_skills = []
    recommendations = {}
    
    for req in required_skills:
        req_lower = req.lower().strip()
        if req_lower in student_skills:
            # Check if tested score is low
            if req in ["Data Structures", "Algorithms", "Coding"] and len(assessments) > 0 and coding_score < 70.0:
                weak_skills.append(req)
                # Include recommendations for weak skills
                recommendations[req] = recommendations_db.get(req, {
                    "course": "Practice code exercises",
                    "project": "Small portfolio challenge",
                    "cert": "General skill validation certificate"
                })
            elif req in ["SQL", "Java", "OOP", "DBMS", "Computer Networks", "Operating Systems"] and len(assessments) > 0 and technical_score < 70.0:
                weak_skills.append(req)
                recommendations[req] = recommendations_db.get(req, {
                    "course": "Practice technical theory",
                    "project": "Small project challenge",
                    "cert": "Technical certificate"
                })
            else:
                strong_skills.append(req)
        else:
            missing_skills.append(req)
            # Generate recommendations for missing skills
            recommendations[req] = recommendations_db.get(req, {
                "course": "Introductory tutorial course",
                "project": "Simple starter project",
                "cert": "Foundational validation certificate"
            })
            
    return {
        "target_role": target_role,
        "strong_skills": strong_skills,
        "weak_skills": weak_skills,
        "missing_skills": missing_skills,
        "recommendations": recommendations
    }
