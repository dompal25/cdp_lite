# src/cdp/segments/ml_engine.py
import json, joblib, numpy as np, pandas as pd
from pathlib import Path
from src.cdp.db import get_con

# ---- Canonical artifact paths (shared with trainer) ----
ROOT = Path(__file__).resolve().parents[3]  # adjust if your package depth differs
ART_DIR = ROOT / "artifacts"
MODEL_PATH = ART_DIR / "model.pkl"
FEATS_PATH = ART_DIR / "feature_list.json"

print("Loading model from:", MODEL_PATH)
print("Loading feature list from:", FEATS_PATH)

def _align_for_inference(df: pd.DataFrame, feature_list: list[str]) -> pd.DataFrame:
    # strip any accidental label columns
    for lbl in ("y", "label", "target"):
        if lbl in df.columns:
            df = df.drop(columns=[lbl])
    # order + fill
    X = df.reindex(columns=feature_list, fill_value=0)
    X = X.replace([np.inf, -np.inf], 0).fillna(0)
    for c in X.columns:
        X[c] = pd.to_numeric(X[c], errors="coerce").fillna(0).astype(float)
    return X

def _load_artifacts():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Missing model at {MODEL_PATH}")
    if not FEATS_PATH.exists():
        raise FileNotFoundError(f"Missing feature list at {FEATS_PATH}")
    model = joblib.load(MODEL_PATH)
    feature_list = json.loads(FEATS_PATH.read_text())
    return model, feature_list

def score_segment(spec: str, limit: int = 25, offset: int = 0):
    con = get_con()

    # ✅ Use your real table
    df = con.sql(f"""
        SELECT *
        FROM features_daily
        LIMIT {int(limit)} OFFSET {int(offset)}
    """).df()

    if df.empty:
        return []

    # keep IDs before aligning
    user_id_col = "user_id" if "user_id" in df.columns else None
    user_ids = df[user_id_col].astype(str).tolist() if user_id_col else [None] * len(df)

    model, feature_list = _load_artifacts()

    # align features to training schema
    feat_df = df.drop(columns=[user_id_col]) if user_id_col else df
    X = _align_for_inference(feat_df, feature_list)
    if X.empty:
        return [{"user_id": uid, "probability": None} for uid in user_ids]

    # predict
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X)[:, 1]
    elif hasattr(model, "decision_function"):
        scores = model.decision_function(X)
        probs = 1 / (1 + np.exp(-scores))
    else:
        probs = model.predict(X).astype(float)

    return [{"user_id": user_ids[i], "probability": float(probs[i])} for i in range(len(user_ids))]
