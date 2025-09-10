from fastapi import APIRouter, Query
from ..segments.registry import SEGMENTS
from ..segments.rules_engine import query_rule_segment
from ..segments.ml_engine import score_segment
from src.cdp.db import get_con

router = APIRouter()

@router.get("/segments")
def list_segments():
    return {"segments": list(SEGMENTS.keys())}

@router.get("/segments/{name}")
def get_segment(name: str, limit: int = Query(100, ge=1, le=10000), offset: int = 0):
    spec = SEGMENTS.get(name)
    if not spec:
        return {"error": f"segment '{name}' not found"}
    if spec["type"] == "rule":
        rows = query_rule_segment(spec, limit=limit, offset=offset)
        return {"name": name, "type": "rule", "items": rows}
    elif spec["type"] == "ml":
        return score_segment(spec, limit=limit, offset=offset)
    else:
        return {"error": "unknown segment type"}

@router.get("/users/{user_id}")
def get_user(user_id: str):
    con = get_connection()
    prof = con.execute("SELECT * FROM profiles WHERE user_id = ?", [user_id]).fetchdf()
    feats = con.execute("SELECT * FROM features_daily WHERE user_id = ?", [user_id]).fetchdf()
    return {
        "profile": prof.to_dict(orient="records")[0] if len(prof) else None,
        "features": feats.to_dict(orient="records")[0] if len(feats) else None,
    }
