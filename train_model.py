import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error
import joblib

def load_dataset(file_path):
    # Handle CSV or XLSX
    ext = os.path.splitext(file_path)[1]
    if ext == '.csv':
        df = pd.read_csv(file_path)
    elif ext == '.xlsx':
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format: Use CSV or XLSX")
    return df

def preprocess_data(df):
    expected_columns = [
        'sem1_internal', 'sem1_mark',
        'sem2_internal', 'sem2_mark',
        'sem3_internal',
        'sem1_attendance', 'sem2_attendance', 'sem3_attendance',
        'sem3_score'  # this is the target
    ]

    # Ensure all expected columns exist
    for col in expected_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    # Fill missing values if any
    df.fillna(0, inplace=True)
    return df

def train_model(file_path):
    df = load_dataset(file_path)
    df = preprocess_data(df)

    features = [

        'sem1_internal', 'sem1_mark',
        'sem2_internal', 'sem2_mark',
    ]
    target = 'sem3_score'

    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("Model trained successfully.")
    print(f"R2 Score: {r2_score(y_test, y_pred):.3f}")
    print(f"Mean Squared Error: {mean_squared_error(y_test, y_pred):.2f}")

    # Save the model in the 'core/ml_model/' directory
    model_save_path = os.path.join('ml_models', 'semester3_score_predictor.pkl')
    joblib.dump(model, model_save_path)
    print(f"Model saved at: {model_save_path}")
    return model

# Example usage
if __name__ == "__main__":
    model = train_model("data/student_data.xlsx")  # or .csv
