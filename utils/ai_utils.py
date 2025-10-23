from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import numpy as np
from collections import Counter
from app import db
from models import LateRecord, SchoolRecord

def train_and_predict_risk():
    """
    Simple AI analytics to predict which students are at high risk of being late again.
    Uses logistic regression based on lateness frequency.
    """
    # Step 1: Collect data
    records = db.session.query(LateRecord.admission_no, LateRecord.date).all()
    if not records:
        return []

    # Step 2: Count lateness frequency per student
    freq = Counter([r.admission_no for r in records])
    students = list(freq.keys())
    X = np.array([[v] for v in freq.values()])  # lateness count
    y = np.array([1 if v > np.mean(list(freq.values())) else 0 for v in freq.values()])  # label high risk if above average

    # Step 3: Scale + train
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = LogisticRegression()
    model.fit(X_scaled, y)

    # Step 4: Predict probability of lateness
    probs = model.predict_proba(X_scaled)[:, 1]  # risk probability

    # Step 5: Merge with student names
    results = []
    for adm, risk in zip(students, probs):
        s = SchoolRecord.query.filter_by(admission_no=adm).first()
        if s:
            results.append({
                "student_name": s.student_name,
                "class_": s.class_,
                "risk": round(float(risk) * 100, 2)
            })

    # Sort by risk descending
    results = sorted(results, key=lambda x: x["risk"], reverse=True)
    return results[:10]
