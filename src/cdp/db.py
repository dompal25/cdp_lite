import os
import duckdb

# Always use the same file-backed database
DB_PATH = "data/cdp.duckdb"
os.makedirs("data", exist_ok=True)

def get_con():
    """Return a DuckDB connection to the shared database file."""
    return duckdb.connect(DB_PATH)