# student.py (Student login route)
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, current_user
from werkzeug.security import check_password_hash
from core.models import User, Performance, StudentDetail  # Ensure Performance and StudentDetail are imported
from core import db

student_bp = Blueprint('student', __name__, url_prefix='/student', template_folder='templates/student')

# Student Login Route
@student_bp.route('/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        student = User.query.filter_by(email=email).first()
        if student and check_password_hash(student.password, password):
            login_user(student)
            flash('Login successful!', 'success')
            return redirect(url_for('student.dashboard'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('student/login.html')

# student.py (Student Dashboard Route)
@student_bp.route('/dashboard')
@login_required
def dashboard():
    # Fetch performance records based on the current logged-in student
    performances = Performance.query.filter_by(student_id=current_user.id).all()
    # Fetch student details (assuming you have a student detail record)
    student_detail = StudentDetail.query.filter_by(user_id=current_user.id).first()

    # Render the dashboard template located at templates/student/dashboard.html
    return render_template('student/dashboard.html', student=current_user, performance_records=performances, student_detail=student_detail)