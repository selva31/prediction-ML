import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import pickle

# Load your dataset
df = pd.read_csv('C:/Users/selva/Downloads/student_performance_data.csv')  # Make sure to adjust the file path

# Step 2: Preprocess (Assuming 'score', 'attendance' are features, and 'grade' is the label)
df = df.dropna()  # Remove rows with missing values
X = df[['score', 'attendance']]  # Feature columns
y = df['grade']  # Target label

# Optional: Convert grades to numeric if needed
# from sklearn.preprocessing import LabelEncoder
# le = LabelEncoder()
# y = le.fit_transform(y)

# Step 3: Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 4: Train model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Step 5: Evaluate
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))

# Step 6: Save the model
joblib.dump(model, 'ml_model.pkl')
print("Model saved as ml_model.pkl")