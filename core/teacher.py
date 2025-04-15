from flask import Blueprint, request, render_template, flash
from flask_login import login_required, current_user
from core.models import Performance, db  # Importing Performance model and db
from core.utils import send_email  # Assuming you have a utility function for sending emails
import pandas as pd

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher', template_folder='templates/teacher')

# Route to upload and predict scores
@teacher_bp.route('/upload', methods=['GET', 'POST'])
# @login_required
def upload():
    if request.method == 'POST':
        # Step 1: Handle CSV upload and prediction
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        if file and file.filename.endswith('.csv'):
            # Read the uploaded CSV file into a DataFrame
            df = pd.read_csv(file)

            # Step 1: Process the CSV to save performance data and trigger alerts
            students = []

            for _, row in df.iterrows():
                student_data = {
                    'student_id': row['student_id'],
                    'score': row['score'],
                    'grade': row['grade']  # Assume there is a 'grade' column in CSV
                }
                students.append(student_data)

                # Save the student's performance into the database
                save_performance(student_data['student_id'], student_data['score'], student_data['grade'])

                # If the score is below 50, trigger a low performance email alert to the teacher
                if student_data['score'] < 50:
                    send_email(
                        'Low Performance Alert',
                        current_user.email,  # Teacher's email
                        'low_score_alert',  # Email template to use
                        teacher_name=current_user.username,
                        student_name=student_data['name'],
                        score=student_data['score']
                    )

            flash('Student performance data uploaded successfully!', 'success')
        else:
            flash('Invalid file format. Please upload a CSV file.', 'danger')

    return render_template('teacher/upload.html')


# Function to save performance data into the database
def save_performance(student_id, score, grade):
    # Create a new performance record
    performance = Performance(
        student_id=student_id,
        score=score,
        grade=grade
    )

    # Add to the session and commit to the database
    db.session.add(performance)
    db.session.commit()
