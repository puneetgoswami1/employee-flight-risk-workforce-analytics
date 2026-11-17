"""
Employee Flight Risk & Workforce Equity Analytics Engine
Author: Puneet Goswami
Description: Computes empirical tenure survival curves (Kaplan-Meier estimator)
             and trains a regularized logistic risk classifier to flag attrition risk.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score


def generate_hris_workforce(n_employees: int = 8000) -> pd.DataFrame:
    """Generates synthetic enterprise HRIS employee records and compensation metrics."""
    np.random.seed(42)

    emp_ids = [f"EMP-{10000 + i}" for i in range(n_employees)]
    role_family = np.random.choice(
        ["Data & Analytics", "Software Engineering", "Product Management", "Cloud Infrastructure"],
        size=n_employees,
        p=[0.30, 0.40, 0.15, 0.15]
    )
    tenure_months = np.random.randint(3, 60, size=n_employees)
    compa_ratio = np.round(np.random.normal(loc=0.96, scale=0.09, size=n_employees).clip(0.72, 1.25), 3)
    months_since_promo = np.minimum(tenure_months, np.random.randint(1, 42, size=n_employees))
    perf_rating = np.random.choice([2, 3, 4, 5], size=n_employees, p=[0.08, 0.52, 0.28, 0.12])
    overtime_index = np.round(np.random.uniform(0.0, 1.0, size=n_employees), 2)

    # Realistic voluntary attrition propensity driven by pay compression + promo lag + burnout
    logits = (
        -2.4
        - 3.8 * (compa_ratio - 0.95)
        + 0.045 * (months_since_promo - 18)
        + 1.15 * (overtime_index - 0.5)
        + 0.55 * ((perf_rating >= 4) & (compa_ratio < 0.88)).astype(float)
    )
    probs = 1 / (1 + np.exp(-logits))
    is_attrited = (np.random.rand(n_employees) < probs).astype(int)

    return pd.DataFrame({
        "employee_id": emp_ids,
        "role_family": role_family,
        "tenure_months": tenure_months,
        "compa_ratio": compa_ratio,
        "months_since_promo": months_since_promo,
        "perf_rating": perf_rating,
        "overtime_index": overtime_index,
        "is_attrited": is_attrited
    })


def compute_survival_and_flight_risk(df: pd.DataFrame):
    """Estimates Kaplan-Meier tenure retention curve and scores active flight risk."""
    print("==========================================================================")
    print("PEOPLE ANALYTICS: TENURE SURVIVAL & ATTRITION RISK BENCHMARK")
    print("==========================================================================")

    # 1. Discrete-Time Kaplan-Meier Survival Curve across 6-month intervals
    checkpoints = [6, 12, 18, 24, 36, 48]
    survival_prob = 1.0
    prev_t = 0

    print("\n--- Empirical Workforce Survival Curve (Retention Probability) ---")
    for t in checkpoints:
        at_risk = (df["tenure_months"] > prev_t).sum()
        events = ((df["tenure_months"] > prev_t) & (df["tenure_months"] <= t) & (df["is_attrited"] == 1)).sum()
        if at_risk > 0:
            survival_prob *= (1.0 - (events / at_risk))
        print(f" - Month {t:2d} Retention Probability : {survival_prob * 100:5.1f}% (At-Risk Cohort: {at_risk:,})")
        prev_t = t

    # 2. Predictive Flight Risk Scoring (Logistic Regression)
    features = ["tenure_months", "compa_ratio", "months_since_promo", "perf_rating", "overtime_index"]
    X = df[features]
    y = df["is_attrited"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression(class_weight="balanced", random_state=42)
    model.fit(X_train_scaled, y_train)

    preds = model.predict(X_test_scaled)
    probs = model.predict_proba(X_test_scaled)[:, 1]

    print("\n--- Flight Risk Model Evaluation ---")
    print(classification_report(y_test, preds, target_names=["Retained", "Voluntary-Exit"]))
    print(f"Discrimination ROC-AUC: {roc_auc_score(y_test, probs):.4f}")

    # Standardized odds impact
    coefs = pd.Series(model.coef_[0], index=features).sort_values(key=abs, ascending=False)
    print("\nStandardized Attrition Risk Drivers (Log-Odds Weight):")
    for feat, weight in coefs.items():
        direction = "Increases Risk" if weight > 0 else "Reduces Risk"
        print(f" - {feat:22s}: {weight:+.3f} ({direction})")


if __name__ == "__main__":
    roster = generate_hris_workforce(8000)
    print(f"Ingested {len(roster):,} HRIS employee records | Baseline Voluntary Attrition: {roster['is_attrited'].mean()*100:.2f}%\n")
    compute_survival_and_flight_risk(roster)