"""app/student/__init__.py — Student blueprint definition."""

from flask import Blueprint

student_bp = Blueprint(
    'student',
    __name__,
    template_folder='templates',
    url_prefix='/student',
)

from app.student import routes  # noqa: F401, E402
from app.student import resume_routes  # noqa: F401, E402
from app.student import assessment_routes  # noqa: F401, E402
from app.student import readiness_routes  # noqa: F401, E402
from app.student import skill_gap_routes  # noqa: F401, E402
from app.student import company_routes  # noqa: F401, E402
from app.student import roadmap_routes  # noqa: F401, E402
from app.student import report_routes  # noqa: F401, E402
from app.student import advisor_routes  # noqa: F401, E402
