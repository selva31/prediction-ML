import pandas as pd
from flask import render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from app.ml_model import predict_scores
from app import app, db
from app.models import Performance, User

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Helper function to check allowed file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files['file']

        # Check if the file is valid
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Read the CSV file and apply predictions
            data = pd.read_csv(filepath)
            predictions = predict_scores(data)

            # Store predictions in database for each student
            for index, row in data.iterrows():
                student = User.query.filter_by(username=row['StudentName']).first()
                if student:
                    performance = Performance(
                        user_id=student.id,
                        score=row['Score'],
                        prediction_category=predictions[index][1]  # Assuming category is in predictions
                    )
                    db.session.add(performance)

            db.session.commit()

            flash("CSV uploaded and predictions made successfully.", "success")
            return render_template('results.html', predictions=predictions)
        else:
            flash("Invalid file format. Please upload a CSV file.", "danger")
    return render_template("upload_performance.html")
