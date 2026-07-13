"""
app/ml/predict.py
──────────────────
Interface to load trained models and make real-time predictions.
"""

import os
import pickle
from typing import Dict, Any

# Resolve absolute paths to ML model pickle files
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'ml_models'))
MODEL_PATH = os.path.join(MODEL_DIR, 'placement_model.pkl')
SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.pkl')


def predict_placement_probability(
    cgpa: float,
    profile_completeness: int,
    resume_score: int,
    quiz_average: float,
    backlogs: int
) -> Dict[str, Any]:
    """
    Load the trained Random Forest model and scaler to compute placement probability.
    
    If the model files do not exist, fall back to a dynamic mathematical calculation.
    """
    # Verify pickle files exist
    if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
        # Fallback calculation if model has not been trained yet
        placement_score = (
            (cgpa - 5.0) / 5.0 * 0.45 +
            (quiz_average / 100.0) * 0.25 +
            (resume_score / 100.0) * 0.15 +
            (profile_completeness / 100.0) * 0.15 -
            (backlogs * 0.1)
        )
        # Convert score to probability percentage
        prob = int(max(10, min(95, placement_score * 100)))
        return {
            "placement_probability": prob,
            "confidence_score": 75,  # Moderate fallback confidence
            "status": "Fallback calculation (Model pickle files missing)"
        }
        
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        with open(SCALER_PATH, 'rb') as f:
            scaler = pickle.load(f)
            
        # Features shape: [[cgpa, completeness, resume, quiz, backlogs]]
        features = [[cgpa, profile_completeness, resume_score, quiz_average, backlogs]]
        features_scaled = scaler.transform(features)
        
        # Calculate probabilities: [prob_unplaced, prob_placed]
        probabilities = model.predict_proba(features_scaled)[0]
        placed_prob = float(probabilities[1])
        
        # Calculate confidence metric based on RF tree variance (mocked estimation)
        confidence = 88.0
        
        return {
            "placement_probability": int(placed_prob * 100),
            "confidence_score": int(confidence),
            "status": "Success"
        }
        
    except Exception as e:
        print(f"Error executing model prediction: {e}")
        return {
            "placement_probability": 50,
            "confidence_score": 50,
            "status": f"Error: {str(e)}"
        }
