import os
import pandas as pd
import joblib
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, login_user
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from flask_mail import Message
from core import db, mail
from core.models import User, PerformanceRecord
from core.forms import LoginForm

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher', template_folder='templates/teacher')

ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@teacher_bp.route('/teacher_login', methods=['GET', 'POST'])
def teacher_login():
    form = LoginForm()
    if form.validate_on_submit():
        teacher = User.query.filter_by(email=form.email.data).first()
        if teacher and check_password_hash(teacher.password, form.password.data):
            login_user(teacher)
            return redirect(url_for('teacher.dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('teacher/login.html', form=form)

@teacher_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'Teacher':
        return redirect(url_for('main.home'))
    total_students = User.query.filter_by(role='Student').count()
    total_performance_records = PerformanceRecord.query.count()
    return render_template('teacher/dashboard.html', total_students=total_students, total_performance_records=total_performance_records)

@teacher_bp.route('/upload_performance', methods=['GET', 'POST'])
@login_required
def upload_performance():
    if current_user.role != 'Teacher':
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        file = request.files.get('file')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_dir = os.path.join('static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)

            if filename.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif filename.endswith('.xlsx'):
                df = pd.read_excel(file_path)

                model = joblib.load('ml_models/semester3_score_predictor.pkl')

            features = df[['sem1_internal', 'sem1_mark','sem2_internal', 'sem2_mark']]
            df['predicted_sem3'] = model.predict(features)

            def categorize(score):
                if score < 40:
                    return 'Low'
                elif 40 <= score <= 65:
                    return 'Average'
                elif 66 <= score <= 85:
                    return 'Good'
                else:
                    return 'Excellent'

            df['category'] = df['predicted_sem3'].apply(categorize)

            PerformanceRecord.query.delete()
            db.session.commit()

            for _, row in df.iterrows():
                student = User.query.filter_by(roll_no=str(row['roll_no'])).first()
                if not student:
                    continue

                record = PerformanceRecord(
                    student_id=student.id,
                    name=row['name'],
                    grade=row['category'],
                    score=row['predicted_sem3'],
                    attendance=row.get('sem3_attendance',)
                )
                db.session.add(record)

                recommendations = []
                if row['predicted_sem3'] < 40:
                    recommendations.append("Attend extra coaching sessions.")
                # if row['attendance'] < 75:
                #     recommendations.append("Improve attendance to meet minimum requirements.")
                if recommendations:
                    send_low_performance_email(student.email, row['category'], recommendations)

            db.session.commit()
            flash('Student performance uploaded and processed successfully!', 'success')
            return redirect(url_for('teacher.view_performance'))
        else:
            flash('Invalid file format. Please upload a CSV or Excel file.', 'danger')

    return render_template('teacher/upload_performance.html')

def send_low_performance_email(student_email, performance, recommendations=None):
    try:
        msg = Message("Low Performance Alert", recipients=[student_email])
        msg.body = f"""
        Dear student,

        We noticed your recent performance shows a low score of {performance} in your recent exams.

        Please meet your academic advisor to get assistance and improve your performance.

        Best regards,
        Academic Support Team
        """
        if recommendations:
            msg.body += "\nRecommendations:\n" + "\n".join(recommendations)
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email to {student_email}: {e}")

@teacher_bp.route('/view_performance')
@login_required
def view_performance():
    performance_records = PerformanceRecord.query.all()

    grade_counts = {'Low': 0, 'Average': 0, 'Good': 0, 'Excellent': 0}
    attendance_groups = {
        'Below 75%': 0,
        '76-80%': 0,
        '81-90%': 0,
        '91-99%': 0
    }

    performance_data = []
    for record in performance_records:
        performance_data.append({
            'name': record.name,
            'score': record.score,
            'attendance': record.attendance,
            'grade': record.grade
        })

        # Initialize attendance group counters
        attendance_groups = {
            'Below 75%': 0,
            '76-80%': 0,
            '81-90%': 0,
            '91-99%': 0
        }

        # Fill attendance groups
        for record in performance_records:
            attendance = record.attendance  # Use the correct field name
            if attendance is None:
                continue  # Skip records without attendance
            if attendance < 75:
                attendance_groups['Below 75%'] += 1
            elif 75 <= attendance <= 80:
                attendance_groups['76-80%'] += 1
            elif 81 <= attendance <= 90:
                attendance_groups['81-90%'] += 1
            else:
                attendance_groups['91-99%'] += 1

        # Initialize grade counts
        grade_counts = {
            'Low': 0,
            'Average': 0,
            'Good': 0,
            'Excellent': 0
        }

        # Count grades using dot notation
        for record in performance_records:
            grade_counts[record.grade] += 1

    # Prepare data for Chart.js
    grade_labels = list(grade_counts.keys())
    grade_values = list(grade_counts.values())

    attendance_labels = list(attendance_groups.keys())
    attendance_values = list(attendance_groups.values())

    return render_template(
        'teacher/view_performance.html',
        performance_records=performance_records,
        performance_data=performance_data,
        grade_counts=dict(grade_counts),
        attendance_groups=attendance_groups,
        grade_labels=grade_labels,
        grade_values=grade_values,
        attendance_labels=attendance_labels,
        attendance_values=attendance_values
    )

@teacher_bp.route('/view_student')
@login_required
def view_student():
    if current_user.role != 'Teacher':
        return redirect(url_for('main.home'))
    students = User.query.filter_by(role='Student').all()
    return render_template('admin/view_student.html', students=students)

@teacher_bp.route('/send_attendance_alerts', methods=['POST'])
@login_required
def send_attendance_alerts():
    students = User.query.filter(User.role == 'Student', User.attendance < 75).all()
    for student in students:
        msg = Message('Attendance Alert', recipients=[student.email])
        msg.body = f"Dear {student.username},\n\nYour attendance is below 75%. Please improve your attendance to avoid academic consequences."
        mail.send(msg)
    flash('Attendance alerts sent to students with low attendance.')
    return redirect(url_for('teacher.view_performance'))

@teacher_bp.route('/send_low_grade_alerts', methods=['POST'])
@login_required
def send_low_grade_alerts():
    low_score_students = PerformanceRecord.query.filter(PerformanceRecord.score < 40).all()

    for student in low_score_students:
        user = User.query.get(student.student_id)
        if user:
            msg = Message(
                'Low Performance Alert',
                sender='selvaqueen333@gmail.com',
                recipients=[user.email]
            )
            msg.body = f'Dear {student.name},\n\nYour performance is below acceptable levels. Please take necessary actions.\n\nRegards,\nAdmin'
            mail.send(msg)

    flash('Low grade alert emails sent successfully!', 'success')
    return redirect(url_for('teacher.view_performance'))
