# utils/ai_utils.py

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from app import db
from models import LateRecord, SchoolRecord

def train_and_predict_risk():
    # Collect data
    records = db.session.query(LateRecord, SchoolRecord).join(
        SchoolRecord, LateRecord.admission_no == SchoolRecord.admission_no
    ).all()

    if not records:
        print("⚠ No records available for training — returning empty risk list.")
        return []

    # Create dummy dataset
    data = []
    for lr, sr in records:
        data.append({
            "student_name": lr.student_name,
            "class_": sr.class_,
            "late_count": 1,
            "risk_label": 0  # simple base case
        })

    df = pd.DataFrame(data)

    if df["risk_label"].nunique() < 2:
     print("⚠ Only one class found in risk_label — skipping ML training.")
     df["predicted_risk"] = 0
     # Ensure a 'risk' field exists for templates
     df["risk"] = 0
     return df.to_dict(orient="records")

# Proceed with model training
    X = df[["late_count"]]
    y = df["risk_label"]

    X_scaled = StandardScaler().fit_transform(X)
    model = LogisticRegression()
    model.fit(X_scaled, y)
    df["predicted_risk"] = model.predict(X_scaled)
    df["risk"] = (df["predicted_risk"] * 100).astype(int)

    return df.to_dict(orient="records")
