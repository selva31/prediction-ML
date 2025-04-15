from flask import Blueprint, render_template
from flask_login import login_required, current_user
from core.models import Performance

student_bp = Blueprint('student', __name__,  url_prefix='/teacher', template_folder='templates/student')

@student_bp.route('/dashboard')
@login_required
def dashboard():
    # Get performance data for the logged-in student
    performances = Performance.query.filter_by(student_id=current_user.id).all()
    return render_template('student/student_dashboard.html', performances=performances)
