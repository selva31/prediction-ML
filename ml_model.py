import pandas as pd
import joblib

# Load the trained model once
model = joblib.load('ml_model.pkl')

def predict_scores(dataframe):
    # Assuming 'score' and 'attendance' are the required columns
    features = dataframe[['score', 'attendance']]
    predictions = model.predict(features)
    dataframe['predicted_grade'] = predictions
    return dataframe
