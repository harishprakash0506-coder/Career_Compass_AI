"""
app/utils/pdf_generator.py
──────────────────────────
Utility module using ReportLab to generate a highly detailed and styled
downloadable PDF report card summarizing student parameters and predictions.
"""

import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

from app.models.student import StudentProfile
from app.utils.readiness_calculator import calculate_comprehensive_readiness
from app.utils.company_matcher import evaluate_company_matches
from app.utils.roadmap_generator import generate_milestone_roadmap


def generate_student_report_pdf(profile: StudentProfile) -> io.BytesIO:
    """
    Generate a styled PDF report using ReportLab containing:
    - Career Readiness Index
    - Placement Predictions (ML probability & confidence)
    - Resume/ATS scores
    - Assessment performance
    - Skill Gap checks
    - Company matches
    - Learning roadmap milestones
    """
    # 1. Fetch parameters
    metrics = calculate_comprehensive_readiness(profile)
    company_matches = evaluate_company_matches(profile)
    roadmap = generate_milestone_roadmap(profile)
    
    # 2. Build PDF Document
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette Matching Design System
    primary_color = colors.HexColor("#4f46e5")
    accent_color = colors.HexColor("#06b6d4")
    dark_bg = colors.HexColor("#0f172a")
    text_color = colors.HexColor("#1e293b")
    text_muted = colors.HexColor("#64748b")
    
    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=text_muted,
        spaceAfter=15
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13.5,
        textColor=text_color,
        spaceAfter=6
    )
    
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=text_color,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    story = []
    
    # Header block
    story.append(Paragraph("CareerCompass AI — Placement Analytics Report", title_style))
    story.append(Paragraph(f"Student: {profile.user.full_name} | Branch: {profile.branch or 'N/A'} | CGPA: {profile.cgpa or 0.0} | Graduation Year: {profile.graduation_year or 'N/A'}", subtitle_style))
    
    # Horizontal Rule
    story.append(Table([[""]], colWidths=[540], rowHeights=[2], style=TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), primary_color),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ])))
    story.append(Spacer(1, 10))
    
    # Core Metrics Table Layout
    metrics_data = [
        [
            Paragraph("<b>Career Readiness Score</b>", body_style),
            Paragraph(f"{metrics['career_readiness_score']}/100", body_style),
            Paragraph("<b>Placement Probability</b>", body_style),
            Paragraph(f"{metrics['placement_probability']}% (ML Predicted)", body_style)
        ],
        [
            Paragraph("<b>Resume ATS Score</b>", body_style),
            Paragraph(f"{metrics['resume_score']}%", body_style),
            Paragraph("<b>Assessment Quiz Avg</b>", body_style),
            Paragraph(f"{metrics['assessment_score']}%", body_style)
        ],
        [
            Paragraph("<b>Profile Completeness</b>", body_style),
            Paragraph(f"{metrics['completeness_score']}%", body_style),
            Paragraph("<b>Active Backlogs</b>", body_style),
            Paragraph(str(profile.backlogs or 0), body_style)
        ]
    ]
    
    metrics_table = Table(metrics_data, colWidths=[150, 120, 150, 120])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    story.append(Paragraph("Unified Score Parameters Summary", section_title_style))
    story.append(metrics_table)
    story.append(Spacer(1, 12))
    
    # Skill Gap Breakdown
    story.append(Paragraph("Preparation Strengths & Recommendations", section_title_style))
    
    story.append(Paragraph("<b>Primary Strengths:</b>", body_style))
    for st in metrics['strengths'][:4]:
        story.append(Paragraph(f"• {st}", bullet_style))
        
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Areas for Improvement:</b>", body_style))
    for wk in metrics['weaknesses'][:4]:
        story.append(Paragraph(f"• {wk}", bullet_style))
    for rec in metrics['recommendations'][:4]:
        story.append(Paragraph(f"• {rec}", bullet_style))
        
    story.append(Spacer(1, 10))
    
    # Company Matches Table Layout
    story.append(Paragraph("Top Target Employer Matching Rankings", section_title_style))
    
    comp_headers = [
        Paragraph("<b>Company</b>", body_style),
        Paragraph("<b>Package Est.</b>", body_style),
        Paragraph("<b>Eligibility</b>", body_style),
        Paragraph("<b>Compatibility Score</b>", body_style)
    ]
    comp_rows = [comp_headers]
    
    for m in company_matches[:5]:
        eligible_text = "Eligible" if m['eligible'] else "Ineligible"
        comp_rows.append([
            Paragraph(m['company_name'], body_style),
            Paragraph(m['package_lpa'], body_style),
            Paragraph(eligible_text, body_style),
            Paragraph(f"{m['match_percentage']}%", body_style)
        ])
        
    comp_table = Table(comp_rows, colWidths=[150, 130, 130, 130])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(comp_table)
    
    # Page Break for Roadmap
    story.append(PageBreak())
    
    # Learning Roadmap timeline milestones
    story.append(Paragraph("Personalized 30-60-90 Day Milestone Roadmap", title_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>30-Day Foundation Milestone:</b>", section_title_style))
    for task in roadmap["plan_30_day"][:4]:
        story.append(Paragraph(f"• {task}", bullet_style))
        
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>60-Day Practical Milestone:</b>", section_title_style))
    for task in roadmap["plan_60_day"][:4]:
        story.append(Paragraph(f"• {task}", bullet_style))
        
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>90-Day Mastery Milestone:</b>", section_title_style))
    for task in roadmap["plan_90_day"][:4]:
        story.append(Paragraph(f"• {task}", bullet_style))
        
    # Build Document
    doc.build(story)
    buffer.seek(0)
    return buffer
