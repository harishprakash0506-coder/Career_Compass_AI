"""
app/utils/resume_parser.py
──────────────────────────
Utility module to parse PDF files and perform ATS scoring analysis.
Does not use external mock APIs; relies on pure Python libraries (PyPDF2)
to parse text and match against specialized skill keywords.
"""

import re
from typing import Dict, List, Any, Tuple
import PyPDF2

# Standard target industry keywords for match analysis
INDUSTRY_KEYWORDS = {
    "languages": ["python", "java", "javascript", "c++", "c#", "golang", "ruby", "rust", "php", "typescript", "swift", "kotlin", "sql", "html", "css"],
    "frameworks_and_tools": ["flask", "django", "react", "angular", "vue", "node", "express", "spring", "docker", "kubernetes", "aws", "gcp", "azure", "git", "jenkins", "terraform"],
    "concepts": ["machine learning", "deep learning", "artificial intelligence", "database", "datastructures", "algorithms", "rest api", "microservices", "oop", "system design", "agile", "devops", "cloud computing"]
}


def extract_text_from_pdf(filepath: str) -> str:
    """Extract text content from a PDF file using PyPDF2."""
    text = ""
    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error parsing PDF file: {e}")
    return text


def analyze_resume_text(text: str) -> Dict[str, Any]:
    """
    Scrutinize the resume text to calculate match scores, missing keywords, and layout suggestions.
    
    Scores are based on:
    - Keywords matches (60%)
    - Structure/Section checks (20%)
    - Formatting checks (20%)
    """
    text_lower = text.lower()
    
    # 1. Keywords Analysis
    found_keywords = []
    missing_keywords = []
    
    for category, keywords in INDUSTRY_KEYWORDS.items():
        for kw in keywords:
            # Match word boundary/substring
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, text_lower):
                found_keywords.append(kw)
            else:
                missing_keywords.append(kw)
                
    # Calculate Keyword Match percentage
    total_expected = sum(len(kws) for kws in INDUSTRY_KEYWORDS.values())
    keyword_score = (len(found_keywords) / total_expected) * 100 if total_expected > 0 else 0
    
    # 2. Section Checks (Structure)
    sections = {
        "education": ["education", "academic", "university", "college", "qualification"],
        "experience": ["experience", "employment", "internship", "work history", "professional history"],
        "skills": ["skills", "expertise", "competencies", "technologies"],
        "projects": ["projects", "personal projects", "academic projects"]
    }
    
    found_sections = []
    missing_sections = []
    for sec_name, keywords in sections.items():
        matched = False
        for kw in keywords:
            if kw in text_lower:
                matched = True
                break
        if matched:
            found_sections.append(sec_name)
        else:
            missing_sections.append(sec_name)
            
    section_score = (len(found_sections) / len(sections)) * 100
    
    # 3. Formatting & General Quality Indicators
    formatting_feedback = []
    format_score = 100
    
    # Contact info check
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    phone_pattern = r'\b\d{10}\b|\b\d{3}[-\s]\d{3}[-\s]\d{4}\b|\+\d{1,2}\s?\d{10}'
    
    if not re.search(email_pattern, text_lower):
        formatting_feedback.append("No email address detected. Ensure your contact info is visible.")
        format_score -= 30
    if not re.search(phone_pattern, text_lower):
        formatting_feedback.append("No telephone number found. Recruiters need a way to reach you.")
        format_score -= 30
        
    # URL check (GitHub/LinkedIn)
    if "linkedin.com" not in text_lower and "github.com" not in text_lower:
        formatting_feedback.append("Consider adding links to your LinkedIn profile or GitHub repositories.")
        format_score -= 20
        
    # Page length indicator (highly simple estimation based on words counts)
    word_count = len(text.split())
    if word_count < 100:
        formatting_feedback.append("Resume content appears very short. Make sure you fully describe your experience.")
        format_score -= 20
        
    format_score = max(0, format_score)
    
    # Add warnings for missing sections
    for sec in missing_sections:
        formatting_feedback.append(f"Missing header: Could not identify a clear '{sec.title()}' section.")
        
    # 4. Composite Scoring
    # Weightage: Keywords (60%), Sections (20%), Formatting (20%)
    ats_score = int((keyword_score * 0.6) + (section_score * 0.2) + (format_score * 0.2))
    ats_score = max(10, min(99, ats_score)) # Clamp between 10 and 99
    
    return {
        "ats_score": ats_score,
        "keyword_score": round(keyword_score, 1),
        "formatting_score": float(format_score),
        "word_count": word_count,
        "found_keywords": found_keywords,
        "missing_keywords": missing_keywords[:8], # Provide top 8 missing
        "formatting_feedback": formatting_feedback if formatting_feedback else ["Format looks neat! Keep it up."]
    }
