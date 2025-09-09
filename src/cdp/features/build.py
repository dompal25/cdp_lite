import duckdb
from src.cdp.db import get_con

def build_features():
    con = get_con()
    con.sql("""
    CREATE OR REPLACE TABLE features_daily AS
    WITH base AS (
        SELECT
            user_id,
            ts,
            event,
            TRY_CAST(json_extract(properties, '$.amount') AS DOUBLE) AS amount
        FROM events
        WHERE ts BETWEEN now() - INTERVAL 30 DAY AND now()
    ),
    agg AS (
        SELECT
            user_id,
            COUNT(*) AS L30D_events,
            COUNT(DISTINCT date_trunc('day', ts)) AS L30D_sessions,
            SUM(CASE WHEN event = 'add_to_cart' THEN 1 ELSE 0 END) AS L30D_add_to_cart,
            SUM(CASE WHEN event = 'purchase'   THEN 1 ELSE 0 END) AS L30D_purchases,
            SUM(CASE WHEN event = 'purchase'   THEN COALESCE(amount,0) ELSE 0 END) AS clv_simple,
            MAX(ts) AS last_event_ts
        FROM base
        GROUP BY 1
    )
    SELECT
        *,
        CASE WHEN L30D_purchases > 0 THEN 1 ELSE 0 END AS y
    FROM agg
    """)
    # optional: print how many rows were built
    print(con.sql("SELECT COUNT(*) AS n FROM features_daily").df())
