import duckdb, json, os, pandas as pd
from src.cdp.db import get_con

def append_events(df: pd.DataFrame):
    # store raw events as parquet & append to DuckDB external table
    con = get_con()
    # Ensure table exists
    con.execute("""
        CREATE TABLE IF NOT EXISTS events (
            event_id TEXT,
            user_id TEXT,
            anonymous_id TEXT,
            event TEXT,
            properties JSON,
            ts TIMESTAMP
        )
    """)
    con.register("events_df", df)
    con.execute("INSERT INTO events SELECT * FROM events_df")
