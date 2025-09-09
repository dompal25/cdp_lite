import duckdb, yaml
from src.cdp.db import get_con

def query_rule_segment(spec: dict, limit=100, offset=0):
    path = spec["file"]
    with open(path, "r", encoding="utf-8") as f:
        rule = yaml.safe_load(f)
    where = rule.get("where", "1=1")
    con = get_con()
    q = f"""
        SELECT user_id
        FROM features_daily
        WHERE {where}
        ORDER BY user_id
        LIMIT {int(limit)} OFFSET {int(offset)}
    """
    return [r[0] for r in con.execute(q).fetchall()]
