import pandas as pd
import pickle
import os

model_path = os.path.join(os.path.dirname(__file__), 'ml/model.pkl')
encoder_path = os.path.join(os.path.dirname(__file__), 'ml/label_encoder.pkl')

with open(model_path, 'rb') as f:
    model = pickle.load(f)

with open(encoder_path, 'rb') as f:
    label_encoder = pickle.load(f)

def predict_scores(filepath):
    ext = os.path.splitext(filepath)[-1].lower()
    if ext == '.csv':
        df = pd.read_csv(filepath)
    elif ext in ['.xls', '.xlsx']:
        df = pd.read_excel(filepath)
    else:
        raise ValueError("Unsupported file type")

    df['total_score'] = df[['math', 'science', 'english']].mean(axis=1)
    X = df[['math', 'science', 'english', 'attendance']]

    preds = model.predict(X)
    categories = label_encoder.inverse_transform(preds)

    results = []
    for i in range(len(df)):
        results.append({
            'name': df.iloc[i].get('name', f'Student {i+1}'),
            'score': df.iloc[i]['total_score'],
            'category': categories[i]
        })
    return results
