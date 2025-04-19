import os
import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# Get the directory of the current script file (train_model.py)
base_dir = os.path.abspath(os.path.dirname(__file__))

# Load your training dataset (you must have this prepared)
df = pd.read_csv(os.path.join(base_dir, 'data', 'semester_scores.csv'))  # Example path

# Example columns: roll_no, name, internal_1, internal_2, internal_3, sem1_mark, sem2_mark, sem3_mark, attendance_1, attendance_2, attendance_3

# Features for training
X = df[['internal_1', 'internal_2', 'sem1_mark', 'sem2_mark', 'attendance_1', 'attendance_2']]
y = df['sem3_mark']

# Train/test split (optional)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Define the path to save the model
model_path = os.path.join(base_dir, 'ml_models', 'sem3_predictor.pkl')

# Save the model
joblib.dump(model, model_path)
print(f"Model trained and saved as {model_path}")
