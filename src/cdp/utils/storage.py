import duckdb, os

DB_PATH = os.getenv("CDP_DB_PATH", "data/warehouse.duckdb")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_con():
    return duckdb.connect(DB_PATH)
