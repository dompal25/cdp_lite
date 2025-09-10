# src/cdp/model/train_propensity.py (or wherever this lives)
import os, json, joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from .metrics import classification_report_df, uplift_by_decile
from src.cdp.db import get_con

ART_DIR = "artifacts"  # match ml_engine loader
os.makedirs(ART_DIR, exist_ok=True)

TARGET = "y"

def train():
    con = get_con()
    df = con.sql("SELECT * FROM features_daily").fetchdf()
    if len(df) < 50:
        raise RuntimeError("Not enough data. Seed more events first.")
    if TARGET not in df.columns:
        raise RuntimeError(f"Missing target column '{TARGET}' in features_daily")

    # --- build X, y (DROP THE TARGET FROM X) ---
    y = df[TARGET].astype(int)
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if TARGET in numeric_cols:
        numeric_cols.remove(TARGET)
    X = df[numeric_cols].fillna(0.0)

    # Safety: ensure we didn’t leak the target
    assert TARGET not in X.columns, "Target leaked into X"

    # --- train ---
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=42
    )
    clf = GradientBoostingClassifier(n_estimators=150, learning_rate=0.08, max_depth=3)
    clf.fit(X_tr, y_tr)

    # --- eval artifacts (optional) ---
    probs = clf.predict_proba(X_te)[:, 1]
    report = classification_report_df(y_te, probs, threshold=0.5)
    uplift = uplift_by_decile(y_te, probs)

    # --- persist model + feature schema + reports ---
    joblib.dump(clf, os.path.join(ART_DIR, "model.pkl"))
    with open(os.path.join(ART_DIR, "feature_list.json"), "w") as f:
        json.dump(numeric_cols, f)

    report.to_csv(os.path.join(ART_DIR, "propensity_report.csv"), index=False)
    uplift.to_csv(os.path.join(ART_DIR, "propensity_uplift.csv"), index=False)

    return {
        "n_train": len(X_tr),
        "n_test": len(X_te),
        "model_path": "artifacts/model.pkl",
        "feature_list_path": "artifacts/feature_list.json",
        "report_path": "artifacts/propensity_report.csv",
    }
