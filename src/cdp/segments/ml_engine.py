import os, duckdb, joblib, pandas as pd
from ..utils.storage import get_connection

ARTIFACT = "data/artifacts/propensity_30d.joblib"
THRESHOLD = 0.6

def score_segment(spec: dict, limit=100, offset=0):
    if not os.path.exists(ARTIFACT):
        return {"error": "model artifact not found. Run: python -m src.cdp.cli train-propensity"}
    model = joblib.load(ARTIFACT)
    con = get_connection()
    feats = con.execute("""
        SELECT user_id, L30D_events, L30D_sessions, L30D_add_to_cart, L30D_purchases, clv_simple
        FROM features_daily
        ORDER BY user_id
        LIMIT ? OFFSET ?
    """, [limit, offset]).fetchdf()
    if feats.empty:
        return {"name": spec.get("name","likely_to_buy_30d"), "type": "ml", "items": []}
    X = feats.drop(columns=["user_id"]).fillna(0.0)
    probs = model.predict_proba(X)[:,1]
    feats["score"] = probs
    feats["in_segment"] = feats["score"] >= spec.get("threshold", THRESHOLD)
    items = feats[feats["in_segment"]]["user_id"].tolist()
    return {"name": "likely_to_buy_30d", "type": "ml", "threshold": spec.get("threshold", THRESHOLD),
            "count": len(items), "items": items[:limit]}
