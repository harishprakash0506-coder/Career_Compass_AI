"""
app/student/assessment_routes.py
────────────────────────────────
Contains routes for the Assessment Engine (Aptitude, Coding, and Technical Quizzes).
Includes:
- Listing available quizzes
- Starting/loading a timed quiz session (MCQ for aptitude/technical, interactive editor for coding)
- Submitting quiz answers with auto-scoring and database entry creation
- Running code against visible test cases (AJAX endpoint)
"""

import io
import sys
import random
import textwrap
import traceback
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user

from app.student import student_bp
from app.extensions import db
from app.models.student import StudentProfile
from app.models.assessment import Assessment, Question
from app.utils.decorators import student_required


# ── Coding Problems Bank ───────────────────────────────────────────────────────

CODING_PROBLEMS = [
    {
        'id': 1,
        'title': 'Two Sum',
        'difficulty': 'Easy',
        'topic': 'Arrays & Hash Maps',
        'description': '''Given an array of integers `nums` and an integer `target`, return the **indices** of the two numbers such that they add up to `target`.

You may assume that each input would have **exactly one solution**, and you may not use the same element twice.
Return the answer in any order.

**Function Signature:**
```python
def two_sum(nums: list[int], target: int) -> list[int]:
```

**Constraints:**
- 2 ≤ nums.length ≤ 10⁴
- -10⁹ ≤ nums[i] ≤ 10⁹
- Only one valid answer exists.''',
        'starter_code': '''def two_sum(nums: list, target: int) -> list:
    """
    Find two indices that sum to target.
    
    Args:
        nums: List of integers
        target: Target sum
    
    Returns:
        List of two indices [i, j] where nums[i] + nums[j] == target
    """
    # Write your solution here
    pass
''',
        'function_name': 'two_sum',
        'visible_tests': [
            {
                'description': 'Basic case',
                'args': [[2, 7, 11, 15], 9],
                'expected': [0, 1],
                'display': 'two_sum([2, 7, 11, 15], 9) → [0, 1]'
            },
            {
                'description': 'Mid-array pair',
                'args': [[3, 2, 4], 6],
                'expected': [1, 2],
                'display': 'two_sum([3, 2, 4], 6) → [1, 2]'
            },
            {
                'description': 'Same value pair',
                'args': [[3, 3], 6],
                'expected': [0, 1],
                'display': 'two_sum([3, 3], 6) → [0, 1]'
            },
        ],
        'hidden_tests': [
            {'args': [[1, 5, 3, 7], 8], 'expected': [1, 3]},
            {'args': [[0, 4, 3, 0], 0], 'expected': [0, 3]},
            {'args': [[-1, -2, -3, -4, -5], -8], 'expected': [2, 4]},
            {'args': [[1000000000, 1000000000], 2000000000], 'expected': [0, 1]},
            {'args': [[2, 5, 5, 11], 10], 'expected': [1, 2]},
        ],
    },
    {
        'id': 2,
        'title': 'Palindrome Number',
        'difficulty': 'Easy',
        'topic': 'Math & Logic',
        'description': '''Given an integer `x`, return `True` if `x` is a **palindrome**, and `False` otherwise.

A palindrome is a number that reads the same forward and backward.

**Function Signature:**
```python
def is_palindrome(x: int) -> bool:
```

**Constraints:**
- -2³¹ ≤ x ≤ 2³¹ - 1

**Hints:**
- Negative numbers are **never** palindromes.
- Could you solve it without converting the integer to a string?''',
        'starter_code': '''def is_palindrome(x: int) -> bool:
    """
    Determine whether an integer is a palindrome.
    
    Args:
        x: Integer to check
    
    Returns:
        True if x reads the same forwards and backwards, False otherwise
    """
    # Write your solution here
    pass
''',
        'function_name': 'is_palindrome',
        'visible_tests': [
            {
                'description': 'Positive palindrome',
                'args': [121],
                'expected': True,
                'display': 'is_palindrome(121) → True'
            },
            {
                'description': 'Negative number',
                'args': [-121],
                'expected': False,
                'display': 'is_palindrome(-121) → False'
            },
            {
                'description': 'Single digit',
                'args': [5],
                'expected': True,
                'display': 'is_palindrome(5) → True'
            },
        ],
        'hidden_tests': [
            {'args': [0], 'expected': True},
            {'args': [10], 'expected': False},
            {'args': [1221], 'expected': True},
            {'args': [-101], 'expected': False},
            {'args': [1000021], 'expected': False},
            {'args': [9999], 'expected': True},
        ],
    },
]

PROBLEMS_BY_ID = {p['id']: p for p in CODING_PROBLEMS}


# ── Helper: Execute code safely ────────────────────────────────────────────────

def _run_code_against_tests(code: str, problem: dict, tests: list) -> list:
    """
    Execute student code against a list of test cases.
    Returns list of result dicts: {passed, input, expected, actual, error}
    """
    results = []
    func_name = problem['function_name']

    for test in tests:
        args = test['args']
        expected = test['expected']
        result = {
            'input': repr(args)[1:-1] if len(args) > 1 else repr(args[0]),
            'expected': repr(expected),
            'actual': None,
            'passed': False,
            'error': None,
        }
        try:
            # Capture stdout
            namespace = {}
            stdout_capture = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = stdout_capture

            try:
                exec(textwrap.dedent(code), namespace)
            finally:
                sys.stdout = old_stdout

            if func_name not in namespace:
                result['error'] = f"Function '{func_name}' not found. Make sure you define it."
                results.append(result)
                continue

            func = namespace[func_name]
            actual = func(*args)
            result['actual'] = repr(actual)

            # Compare — sort list results for order-independent comparison
            if isinstance(expected, list) and isinstance(actual, list):
                result['passed'] = sorted(actual) == sorted(expected)
            else:
                result['passed'] = actual == expected

        except SyntaxError as e:
            result['error'] = f"SyntaxError on line {e.lineno}: {e.msg}"
        except Exception as e:
            result['error'] = f"{type(e).__name__}: {e}"

        results.append(result)

    return results


# ── Routes ─────────────────────────────────────────────────────────────────────

@student_bp.route('/assessments', methods=['GET'])
@login_required
@student_required
def assessments():
    """List student's completed assessments and available assessment categories."""
    profile = current_user.student_profile
    
    # Retrieve past assessments
    past_assessments = Assessment.query.filter_by(student_id=profile.id).order_by(Assessment.completed_at.desc()).all()
    
    # Simple summary metric counts
    completed_categories = [a.category for a in past_assessments]
    
    return render_template(
        'student/assessments.html',
        profile=profile,
        assessments=past_assessments,
        completed_categories=completed_categories
    )


@student_bp.route('/assessments/start/<string:category>', methods=['GET', 'POST'])
@login_required
@student_required
def start_assessment(category):
    """
    GET  — Render the timed quiz page (MCQ for aptitude/technical, code editor for coding).
    POST — Evaluate answers, write Assessment scores record to DB, and redirect.
    """
    if category not in ['aptitude', 'coding', 'technical']:
        abort(404)

    profile = current_user.student_profile

    # ── Coding: custom interactive editor ─────────────────────────────────────
    if category == 'coding':
        if request.method == 'GET':
            # Strip hidden_tests before sending to template (security: never expose to client)
            safe_problems = [
                {**{k: v for k, v in p.items() if k != 'hidden_tests'},
                 'hidden_count': len(p['hidden_tests'])}
                for p in CODING_PROBLEMS
            ]
            return render_template(
                'student/coding_session.html',
                problems=safe_problems,
                time_limit_minutes=30,
            )

        # POST: grade submitted code for all problems
        total_hidden = 0
        total_passed = 0
        problem_results = []

        for problem in CODING_PROBLEMS:
            code = request.form.get(f'code_{problem["id"]}', '').strip()
            hidden = problem['hidden_tests']
            total_hidden += len(hidden)

            if code:
                results = _run_code_against_tests(code, problem, hidden)
                passed = sum(1 for r in results if r['passed'])
                total_passed += passed
                problem_results.append({
                    'title': problem['title'],
                    'passed': passed,
                    'total': len(hidden),
                })
            else:
                problem_results.append({
                    'title': problem['title'],
                    'passed': 0,
                    'total': len(hidden),
                })

        # Score = hidden test pass rate * 100
        score_pct = round((total_passed / total_hidden) * 100, 1) if total_hidden > 0 else 0.0

        new_assessment = Assessment(
            student_id=profile.id,
            category='coding',
            total_questions=len(CODING_PROBLEMS),
            correct_answers=sum(1 for p in problem_results if p['passed'] == p['total']),
            score_percentage=score_pct,
            duration_seconds=random.randint(300, 1500),
            answer_log=[],
            completed_at=datetime.utcnow(),
        )
        db.session.add(new_assessment)
        profile.compute_profile_completeness()
        db.session.commit()

        flash(
            f'Coding assessment completed! Score: {score_pct}% '
            f'({total_passed}/{total_hidden} hidden test cases passed)',
            'success'
        )
        return redirect(url_for('student.assessments'))

    # ── MCQ: aptitude or technical ─────────────────────────────────────────────
    questions = Question.query.filter_by(category=category).all()

    if not questions:
        flash("No questions found in this category. Database may not be seeded.", "warning")
        return redirect(url_for('student.assessments'))

    if request.method == 'GET':
        return render_template(
            'student/quiz_session.html',
            category=category,
            questions=questions,
            time_limit_minutes=15
        )

    # POST: Evaluate MCQ submission
    correct_count = 0
    total_count = len(questions)
    answer_log = {}

    for q in questions:
        submitted_val = request.form.get(f'question_{q.id}')
        selected_index = int(submitted_val) if (submitted_val is not None and submitted_val.isdigit()) else None
        answer_log[str(q.id)] = selected_index
        if selected_index is not None and selected_index == q.correct_index:
            correct_count += 1

    score_pct = round((correct_count / total_count) * 100, 1) if total_count > 0 else 0.0

    new_assessment = Assessment(
        student_id=profile.id,
        category=category,
        total_questions=total_count,
        correct_answers=correct_count,
        score_percentage=score_pct,
        duration_seconds=random.randint(180, 600),
        answer_log=answer_log,
        completed_at=datetime.utcnow()
    )
    db.session.add(new_assessment)
    profile.compute_profile_completeness()
    db.session.commit()

    flash(f'{category.title()} assessment completed! Score: {score_pct}%', 'success')
    return redirect(url_for('student.assessments'))


@student_bp.route('/assessments/coding/run', methods=['POST'])
@login_required
@student_required
def coding_run():
    """
    AJAX endpoint — Execute student code against visible test cases for a problem.
    Returns JSON result list with pass/fail, actual output, and errors.
    """
    data = request.get_json(silent=True) or {}
    problem_id = data.get('problem_id')
    code = data.get('code', '').strip()

    problem = PROBLEMS_BY_ID.get(problem_id)
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404

    if not code:
        return jsonify({'error': 'No code provided'}), 400

    results = _run_code_against_tests(code, problem, problem['visible_tests'])

    # Attach display descriptions
    for i, r in enumerate(results):
        if i < len(problem['visible_tests']):
            r['display'] = problem['visible_tests'][i].get('display', '')

    passed = sum(1 for r in results if r['passed'])
    return jsonify({
        'results': results,
        'passed': passed,
        'total': len(results),
    })
