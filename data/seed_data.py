"""
data/seed_data.py
──────────────────
Database seeder — run once after `python run.py` creates the schema.

Creates:
  • 1 Admin user
  • 1 Placement Officer
  • 200 Student accounts, each with a randomised StudentProfile
  • 600 Assessments (3 per student, one per category)
  • 180 PlacementRecords (for 90% of students, randomised status)

Usage:
    python data/seed_data.py
"""

import sys
import os
import random
import json
from datetime import datetime, timedelta, date

# ── Resolve project root so imports work ──────────────────────────────
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, '.env'))

from app import create_app
from app.extensions import db
from app.models.user import User, Role
from app.models.student import StudentProfile
from app.models.assessment import Assessment, Question
from app.models.placement import PlacementRecord

# ── Constants ─────────────────────────────────────────────────────────
BRANCHES = [
    'Computer Science & Engineering',
    'Information Technology',
    'Electronics & Communication Engineering',
    'Mechanical Engineering',
    'Civil Engineering',
    'Electrical Engineering',
]

SKILLS_POOL = [
    'Python', 'Java', 'C++', 'JavaScript', 'SQL', 'Machine Learning',
    'Deep Learning', 'Data Structures', 'Algorithms', 'React', 'Node.js',
    'Flask', 'Django', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy',
    'Git', 'Docker', 'Linux', 'REST APIs', 'HTML', 'CSS', 'MongoDB',
    'PostgreSQL', 'AWS', 'Azure', 'Computer Networks', 'DBMS', 'OOP',
]

COMPANIES = [
    'TCS', 'Infosys', 'Wipro', 'HCL Technologies', 'Cognizant',
    'Accenture', 'Capgemini', 'Tech Mahindra', 'Hexaware', 'Mphasis',
    'Amazon', 'Google', 'Microsoft', 'Flipkart', 'Paytm',
]

ROLES_BY_COMPANY = {
    'Amazon':    'SDE Intern',
    'Google':    'Software Engineering Intern',
    'Microsoft': 'Program Manager Intern',
    'Flipkart':  'SDE I',
    'Paytm':     'Software Engineer',
}
DEFAULT_ROLE = 'Software Engineer'

FIRST_NAMES = [
    'Aarav', 'Aditi', 'Arjun', 'Ananya', 'Bhavya', 'Chetan', 'Divya',
    'Dhruv', 'Esha', 'Farhan', 'Gayatri', 'Harsh', 'Ishaan', 'Jyoti',
    'Karan', 'Kavya', 'Lakshmi', 'Manav', 'Nisha', 'Om', 'Pooja',
    'Rahul', 'Riya', 'Sanjay', 'Sneha', 'Tanvi', 'Uday', 'Vidya',
    'Yash', 'Zara',
]
LAST_NAMES = [
    'Sharma', 'Verma', 'Patel', 'Gupta', 'Singh', 'Kumar', 'Mehta',
    'Shah', 'Joshi', 'Nair', 'Iyer', 'Reddy', 'Rao', 'Das', 'Malhotra',
]

SAMPLE_QUESTIONS = [
    # Aptitude
    {
        'category': 'aptitude', 'difficulty': 'easy',
        'topic': 'Percentage',
        'text': 'What is 15% of 200?',
        'options': ['25', '30', '35', '20'],
        'correct_index': 1,
        'explanation': '15% of 200 = 0.15 × 200 = 30.',
    },
    {
        'category': 'aptitude', 'difficulty': 'medium',
        'topic': 'Probability',
        'text': 'A bag contains 3 red and 5 blue balls. What is the probability of picking a red ball?',
        'options': ['3/8', '5/8', '1/3', '3/5'],
        'correct_index': 0,
        'explanation': 'P(red) = 3 / (3+5) = 3/8.',
    },
    {
        'category': 'aptitude', 'difficulty': 'hard',
        'topic': 'Time & Work',
        'text': 'A can do a job in 12 days and B in 18 days. In how many days can they finish it together?',
        'options': ['7.2', '6.5', '7.5', '8'],
        'correct_index': 0,
        'explanation': 'Combined rate = 1/12 + 1/18 = 5/36 per day. Days = 36/5 = 7.2.',
    },
    # Coding
    {
        'category': 'coding', 'difficulty': 'easy',
        'topic': 'Arrays',
        'text': 'What is the time complexity of accessing an element in an array by index?',
        'options': ['O(1)', 'O(n)', 'O(log n)', 'O(n²)'],
        'correct_index': 0,
        'explanation': 'Array index access is constant time O(1).',
    },
    {
        'category': 'coding', 'difficulty': 'medium',
        'topic': 'Sorting',
        'text': 'What is the average time complexity of Quick Sort?',
        'options': ['O(n log n)', 'O(n²)', 'O(n)', 'O(log n)'],
        'correct_index': 0,
        'explanation': 'Quick Sort has average-case O(n log n) and worst-case O(n²).',
    },
    {
        'category': 'coding', 'difficulty': 'hard',
        'topic': 'Dynamic Programming',
        'text': 'Which technique does the Longest Common Subsequence problem use?',
        'options': ['Dynamic Programming', 'Greedy', 'Divide and Conquer', 'Backtracking'],
        'correct_index': 0,
        'explanation': 'LCS is a classic Dynamic Programming problem with O(mn) time complexity.',
    },
    # Technical
    {
        'category': 'technical', 'difficulty': 'easy',
        'topic': 'Databases',
        'text': 'Which SQL keyword is used to retrieve unique values?',
        'options': ['DISTINCT', 'UNIQUE', 'DIFFERENT', 'ONLY'],
        'correct_index': 0,
        'explanation': 'SELECT DISTINCT eliminates duplicate rows from the result set.',
    },
    {
        'category': 'technical', 'difficulty': 'medium',
        'topic': 'Networking',
        'text': 'What does HTTP stand for?',
        'options': [
            'HyperText Transfer Protocol',
            'High Transfer Text Protocol',
            'HyperText Transmission Protocol',
            'Hybrid Transfer Text Protocol',
        ],
        'correct_index': 0,
        'explanation': 'HTTP = HyperText Transfer Protocol, used for web communication.',
    },
    {
        'category': 'technical', 'difficulty': 'hard',
        'topic': 'Operating Systems',
        'text': 'In the context of OS scheduling, what does "starvation" mean?',
        'options': [
            'A process never gets CPU time due to priority',
            'CPU usage drops to 0%',
            'Memory is fully consumed',
            'Deadlock between two processes',
        ],
        'correct_index': 0,
        'explanation': 'Starvation occurs when low-priority processes are perpetually denied CPU time.',
    },
]


def _random_name() -> str:
    return f'{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}'


def _random_email(name: str, idx: int) -> str:
    slug = name.lower().replace(' ', '.').replace("'", '')
    return f'{slug}.{idx:03d}@student.edu'


def _random_cgpa() -> float:
    return round(random.gauss(7.5, 1.0), 2).__abs__()


def _random_skills(n: int = 6) -> list:
    return random.sample(SKILLS_POOL, min(n, len(SKILLS_POOL)))


def _random_projects(n: int = 2) -> list:
    project_names = [
        'E-Commerce Platform', 'Weather App', 'Chat Application',
        'Expense Tracker', 'Portfolio Website', 'Inventory System',
        'Student Management System', 'Sentiment Analyzer', 'Image Classifier',
    ]
    techs = ['Python', 'Flask', 'React', 'Node.js', 'MongoDB', 'MySQL', 'TensorFlow']
    return [
        {
            'title':        random.choice(project_names),
            'description':  'A full-stack web application with REST API.',
            'technologies': random.sample(techs, 3),
            'url':          'https://github.com/example/project',
            'duration':     f'{random.randint(1, 6)} months',
        }
        for _ in range(n)
    ]


def _random_internship() -> list:
    companies = ['Infosys', 'TCS BPS', 'Wipro', 'HCL', 'IBM', 'BSNL', 'Startups']
    return [
        {
            'company':     random.choice(companies),
            'role':        'Software Development Intern',
            'duration':    f'{random.randint(1, 6)} months',
            'description': 'Developed features for internal tools using Python and REST APIs.',
            'stipend':     f'{random.randint(5, 30)}k/month',
        }
    ]


def _random_certifications() -> list:
    certs = [
        {'name': 'AWS Cloud Practitioner', 'issuer': 'Amazon', 'date': '2024-01-15', 'credential_url': ''},
        {'name': 'Google Data Analytics', 'issuer': 'Google', 'date': '2023-11-20', 'credential_url': ''},
        {'name': 'Python for Everybody',  'issuer': 'Coursera', 'date': '2023-08-10', 'credential_url': ''},
    ]
    return random.sample(certs, random.randint(0, 2))


def _random_assessment_score(category: str) -> float:
    means = {'aptitude': 68, 'coding': 62, 'technical': 70}
    score = random.gauss(means.get(category, 65), 15)
    return round(max(0.0, min(100.0, score)), 2)


def seed_database():
    """Drop all tables, recreate, and seed with synthetic data."""
    app = create_app('development')

    with app.app_context():
        db.drop_all()
        db.create_all()
        print('[seed] Tables created.')

        # ── 1. Question Bank ────────────────────────────────────────────
        for q_data in SAMPLE_QUESTIONS:
            q = Question(
                category=q_data['category'],
                difficulty=q_data['difficulty'],
                topic=q_data['topic'],
                text=q_data['text'],
                correct_index=q_data['correct_index'],
                explanation=q_data.get('explanation', ''),
            )
            q.options = q_data['options']
            db.session.add(q)
        db.session.flush()
        print(f'[seed] {len(SAMPLE_QUESTIONS)} questions inserted.')

        # ── 2. Admin User ───────────────────────────────────────────────
        admin = User(full_name='Admin User', email='admin@careercompass.ai', role=Role.ADMIN)
        admin.set_password('Admin@2025!')
        db.session.add(admin)

        # ── 3. Placement Officer ────────────────────────────────────────
        officer = User(full_name='Dr. Priya Nair', email='officer@careercompass.ai', role=Role.OFFICER)
        officer.set_password('Officer@2025!')
        db.session.add(officer)

        db.session.flush()
        print('[seed] Admin and Officer created.')

        # ── 4. Students ─────────────────────────────────────────────────
        for i in range(1, 201):
            name  = _random_name()
            email = _random_email(name, i)
            cgpa  = max(5.0, min(10.0, _random_cgpa()))

            student = User(full_name=name, email=email, role=Role.STUDENT)
            student.set_password('Student@123')
            db.session.add(student)
            db.session.flush()  # get student.id

            branch = random.choice(BRANCHES)
            year   = random.randint(3, 4)
            grad_y = 2025 if year == 4 else 2026

            profile = StudentProfile(
                user_id=student.id,
                phone=f'9{random.randint(100_000_000, 999_999_999)}',
                date_of_birth=date(random.randint(2000, 2003), random.randint(1, 12), random.randint(1, 28)),
                gender=random.choice(['male', 'female']),
                college_name='National Institute of Technology',
                branch=branch,
                year_of_study=year,
                graduation_year=grad_y,
                cgpa=round(cgpa, 2),
                backlogs=random.choices([0, 1, 2, 3], weights=[70, 15, 10, 5])[0],
                tenth_percentage=round(random.uniform(65, 98), 1),
                twelfth_percentage=round(random.uniform(60, 98), 1),
                linkedin_url=f'https://linkedin.com/in/{name.lower().replace(" ", "-")}-{i}',
                github_url=f'https://github.com/{name.lower().replace(" ", "")}{i}',
                resume_filename=f'resume_{student.id}.pdf' if random.random() > 0.3 else None,
                resume_uploaded_at=datetime.utcnow() - timedelta(days=random.randint(1, 90)),
            )
            profile.skills        = _random_skills(random.randint(4, 10))
            profile.projects      = _random_projects(random.randint(1, 3))
            profile.internships   = _random_internship() if random.random() > 0.4 else []
            profile.certifications = _random_certifications()
            profile.compute_profile_completeness()
            db.session.add(profile)
            db.session.flush()  # get profile.id

            # ── 5. Assessments (3 per student) ──────────────────────────
            for cat in ['aptitude', 'coding', 'technical']:
                score = _random_assessment_score(cat)
                started = datetime.utcnow() - timedelta(days=random.randint(1, 60))
                assessment = Assessment(
                    student_id=profile.id,
                    category=cat,
                    total_questions=10,
                    correct_answers=round(score / 10),
                    score_percentage=score,
                    duration_seconds=random.randint(300, 1800),
                    started_at=started,
                    completed_at=started + timedelta(minutes=random.randint(10, 30)),
                )
                db.session.add(assessment)

            # ── 6. Placement Records (90% of students) ──────────────────
            if random.random() < 0.90:
                company = random.choice(COMPANIES)
                role    = ROLES_BY_COMPANY.get(company, DEFAULT_ROLE)
                # Placement probability based on CGPA
                placed  = cgpa >= 7.0 and random.random() < 0.82
                status  = 'selected' if placed else random.choice(['applied', 'shortlisted', 'rejected'])
                package = round(random.uniform(3.5, 25.0), 2) if status == 'selected' else None

                record = PlacementRecord(
                    student_id=profile.id,
                    company_name=company,
                    role=role,
                    package_lpa=package,
                    status=status,
                    applied_at=datetime.utcnow() - timedelta(days=random.randint(1, 180)),
                )
                db.session.add(record)

        db.session.commit()
        print('[seed] 200 students, 600 assessments, ~180 placement records seeded.')
        print('[seed] ✓ Database ready.')
        print()
        print('  Admin    : admin@careercompass.ai   / Admin@2025!')
        print('  Officer  : officer@careercompass.ai / Officer@2025!')
        print('  Students : <name>@student.edu       / Student@123')


if __name__ == '__main__':
    seed_database()
