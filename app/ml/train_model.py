"""
app/ml/train_model.py
─────────────────────
Generates a synthetic placement dataset, trains a Random Forest Classifier
using academic parameters, assessment scores, and resume criteria as features,
and saves the trained model and scaler as pickle files.
"""

import os
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler


def generate_synthetic_dataset(num_records: int = 1000) -> pd.DataFrame:
    """
    Generate a balanced synthetic dataset representing student placement profiles.
    
    Features:
    - cgpa: float (4.0 to 10.0)
    - profile_completeness: int (0 to 100)
    - resume_score: int (0 to 100)
    - quiz_average: float (0 to 100)
    - backlogs: int (0 to 5)
    
    Target:
    - placed: int (0 or 1)
    """
    np.random.seed(42)
    
    cgpa = np.random.uniform(5.5, 9.8, num_records)
    profile_completeness = np.random.randint(40, 100, num_records)
    resume_score = np.random.randint(30, 98, num_records)
    quiz_average = np.random.uniform(40, 95, num_records)
    backlogs = np.random.choice([0, 1, 2, 3], size=num_records, p=[0.7, 0.18, 0.08, 0.04])
    
    # Calculate a composite placement index to determine target label
    # High weight on CGPA, Quiz Average, and low backlogs
    placement_score = (
        (cgpa - 5.5) / 4.3 * 0.45 +
        (quiz_average - 40) / 55 * 0.25 +
        (resume_score - 30) / 68 * 0.15 +
        (profile_completeness - 40) / 60 * 0.05 -
        (backlogs * 0.15)
    )
    
    # Add minor random noise
    placement_score += np.random.normal(0, 0.08, num_records)
    
    # Classify as placed if score exceeds threshold
    placed = (placement_score > 0.35).astype(int)
    
    # Pack into dataframe
    df = pd.DataFrame({
        'cgpa': cgpa,
        'profile_completeness': profile_completeness,
        'resume_score': resume_score,
        'quiz_average': quiz_average,
        'backlogs': backlogs,
        'placed': placed
    })
    return df


def train_placement_model():
    """Train Random Forest Classifier and save it as a pickle file."""
    # Ensure target output directory exists
    model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'ml_models'))
    os.makedirs(model_dir, exist_ok=True)
    
    # Generate data
    df = generate_synthetic_dataset(1200)
    
    X = df[['cgpa', 'profile_completeness', 'resume_score', 'quiz_average', 'backlogs']]
    y = df['placed']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Feature scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest model
    clf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    clf.fit(X_train_scaled, y_train)
    
    # Print accuracy metric
    train_acc = clf.score(X_train_scaled, y_train)
    test_acc = clf.score(X_test_scaled, y_test)
    print(f"[ML Engine] Training complete. Train Accuracy: {train_acc:.2%}, Test Accuracy: {test_acc:.2%}")
    
    # Save objects to pickle files
    model_path = os.path.join(model_dir, 'placement_model.pkl')
    scaler_path = os.path.join(model_dir, 'scaler.pkl')
    
    with open(model_path, 'wb') as f:
        pickle.dump(clf, f)
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
        
    print(f"[ML Engine] Model exported to: {model_path}")
    print(f"[ML Engine] Scaler exported to: {scaler_path}")


if __name__ == '__main__':
    train_placement_model()
