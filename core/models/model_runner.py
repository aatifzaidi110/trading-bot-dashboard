# core/models/model_runner.py

import pandas as pd
import numpy as np
import joblib
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

# Load model once
try:
    model = joblib.load(MODEL_PATH)
except Exception:
    model = None

def enhance_with_ml(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enhances the dataframe with model predictions.

    Expects model.pkl to predict a binary signal or confidence score.
    """
    if model is None or df.empty:
        df["ml_prediction"] = 0
        return df

    feature_cols = ["open", "high", "low", "close", "volume"]
    input_df = df[feature_cols].copy()

    try:
        preds = model.predict_proba(input_df)[:, 1]  # assuming binary classification
    except:
        preds = np.zeros(len(df))

    df["ml_prediction"] = preds
    return df
