import duckdb, pandas as pd
from ..utils.storage import get_connection

def resolve_identities():
    con = get_connection()
    # very simple: user_id if present else anonymous_id as stable id
    con.execute("""
        CREATE TABLE IF NOT EXISTS profiles AS
        SELECT DISTINCT
            COALESCE(user_id, anonymous_id) AS user_id,
            MIN(ts) AS first_seen,
            MAX(ts) AS last_seen
        FROM events
        GROUP BY 1
    """)
    # add email/phone if present in identify traits
    try:
        con.execute("""
            ALTER TABLE profiles ADD COLUMN IF NOT EXISTS email TEXT;
            ALTER TABLE profiles ADD COLUMN IF NOT EXISTS phone TEXT;
        """)
    except Exception:
        pass
