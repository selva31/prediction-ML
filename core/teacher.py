import os
import pandas as pd
import joblib
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, login_user
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from flask_mail import Message
from core import db, mail
from core.models import User, Performance, PerformanceRecord
from core.forms import LoginForm
import matplotlib.pyplot as plt
import io
import base64

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher', template_folder='templates/teacher')

# Define the allowed file extensions
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Teacher login route
@teacher_bp.route('/teacher_login', methods=['GET', 'POST'])
def teacher_login():
    form = LoginForm()
    if form.validate_on_submit():
        teacher = User.query.filter_by(email=form.email.data).first()
        if teacher:
            # Check if the password matches the hashed password
            if check_password_hash(teacher.password, form.password.data):
                login_user(teacher)
                return redirect(url_for('teacher.dashboard'))  # Redirect after successful login
            else:
                flash('Invalid email or password', 'danger')
        else:
            flash('Invalid email or password', 'danger')
    return render_template('teacher/login.html', form=form)



# Teacher dashboard
@teacher_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'Teacher':
        return redirect(url_for('main.index'))  # Redirect non-teachers

    total_students = User.query.filter_by(role='Student').count()
    total_performance_records = Performance.query.count()

    return render_template('teacher/dashboard.html',
                           total_students=total_students,
                           total_performance_records=total_performance_records)


# Upload and predict performance
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

            # Read the file
            if filename.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif filename.endswith('.xlsx'):
                df = pd.read_excel(file_path)

            # Load model
            model = joblib.load('ml_models/sem3_predictor.pkl')

            # Predict using selected features
            features = df[['internal_1', 'internal_2', 'sem1_mark', 'sem2_mark', 'attendance_1', 'attendance_2']]
            df['predicted_sem3'] = model.predict(features)

            # Categorize performance
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

            # Save predictions to database
            for _, row in df.iterrows():
                student = User.query.filter_by(roll_no=row['roll_no']).first()
                if not student:
                    print(f"Student with roll number {row['roll_no']} not found. Skipping.")
                    continue

                record = PerformanceRecord(
                    student_id=student.id,
                    name=row['name'],
                    grade=row['category'],
                    score=row['predicted_sem3']
                )
                db.session.add(record)

            # Alert: send email for low performance or low attendance
                student = User.query.filter_by(roll_no=str(row['roll_no'])).first()
                if student:
                    recommendations = []
                    if row['predicted_sem3'] < 40:
                        recommendations.append("Attend extra coaching sessions.")
                    if row['attendance_1'] < 75 or row['attendance_2'] < 75 or row['attendance_3'] < 75:
                        recommendations.append("Improve attendance to meet minimum requirements.")
                    if recommendations:
                        send_low_performance_email(student.email, row['category'], recommendations)

            db.session.commit()

            flash('Student performance uploaded and processed successfully!', 'success')
            return redirect(url_for('teacher.view_performance'))
        else:
            flash('Invalid file format. Please upload a CSV or Excel file.', 'danger')

    return render_template('teacher/upload_performance.html')

# Categorize performance based on the score
def categorize_performance(score):
    if score < 40:
        return 'Low'
    elif 41 <= score <= 65:
        return 'Average'
    elif 66 <= score <= 85:
        return 'Good'
    else:
        return 'Excellent'


# Prediction logic (dummy function, use actual model)
def predict_student_performance(df):
    # Example: dummy prediction, replace with actual model loading and prediction
    return df['score'] * 0.9  # Fake calculation


# Generate progress tracker chart
def generate_progress_chart(df):
    fig, ax = plt.subplots()
    ax.bar(df['student_id'], df['Prediction'])
    ax.set_xlabel('Student ID')
    ax.set_ylabel('Predicted Score')

    # Save the chart as PNG in memory and encode to base64
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_b64 = base64.b64encode(img.read()).decode('utf-8')

    return f"data:image/png;base64,{img_b64}"


# Send email alert for low performance
def send_low_performance_email(student_email, performance, recommendations=None):
    msg = Message("Low Performance Alert", recipients=[student_email])
    msg.body = f"Dear Student, your performance is categorized as {performance}. Please review your study materials."
    if recommendations:
        msg.body += "\nRecommendations:\n" + "\n".join(recommendations)
    mail.send(msg)


# View performance
@teacher_bp.route('/view_performance')
@login_required
def view_performance():
    records = PerformanceRecord.query.all()

    # Count grades for Chart.js
    grade_counts = {
        'Low': 0,
        'Average': 0,
        'Good': 0,
        'Excellent': 0
    }

    for record in records:
        if record.grade in grade_counts:
            grade_counts[record.grade] += 1

    return render_template('teacher/view_performance.html', performance_records=records, grade_counts=grade_counts)


# Teacher dashboard page for viewing students' progress
# View all students (for Teacher role)
@teacher_bp.route('/view_student')
@login_required
def view_student():
    if current_user.role != 'Teacher':
        return redirect(url_for('main.home'))  # Redirect non-teachers to the home page

    # Fetch all students
    students = User.query.filter_by(role='Student').all()

    # Render the view_student template from admin folder
    return render_template('admin/view_student.html', students=students)


# Add recommendations based on performance
def get_recommendations(score):
    if score < 40:
        return ["Khan Academy: Math Basics", "YouTube: Basic Algebra"]
    return []


def send_attendance_alert(student_email):
    msg = Message("Attendance Alert", recipients=[student_email])
    msg.body = "Dear Student, your attendance is below 75%. Please ensure better attendance to avoid issues."
    mail.send(msg)


