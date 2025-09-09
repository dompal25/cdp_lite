import os, duckdb, joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from .metrics import classification_report_df, uplift_by_decile
from src.cdp.db import get_con


ART_DIR = "data/artifacts"
os.makedirs(ART_DIR, exist_ok=True)


def train():
    con = get_con()
    df = con.sql("SELECT * FROM features_daily").fetchdf()  
    if len(df) < 50:
        raise RuntimeError("Not enough data. Seed more events first.")

    numeric = df.select_dtypes(include=["number"]).columns
    X = df[numeric].fillna(0.0)
    y = df["y"].astype(int)

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, stratify=y, random_state=42)
    clf = GradientBoostingClassifier(n_estimators=150, learning_rate=0.08, max_depth=3)
    clf.fit(X_tr, y_tr)
    probs = clf.predict_proba(X_te)[:,1]
    report = classification_report_df(y_te, probs, threshold=0.5)
    uplift = uplift_by_decile(y_te, probs)
    joblib.dump(clf, os.path.join(ART_DIR, "propensity_30d.joblib"))
    report.to_csv(os.path.join(ART_DIR, "propensity_report.csv"), index=False)
    uplift.to_csv(os.path.join(ART_DIR, "propensity_uplift.csv"), index=False)
    return {"n_train": len(X_tr), "n_test": len(X_te), "report_path": "data/artifacts/propensity_report.csv"}
