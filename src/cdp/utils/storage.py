import duckdb, os
from src.cdp.db import get_con  # just re-export

# nothing else needed here unless you want helper functions later


DB_PATH = os.getenv("CDP_DB_PATH", "data/warehouse.duckdb")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_con():
    return duckdb.connect(DB_PATH)
