import os, random, string
import pandas as pd
from datetime import datetime, timedelta, timezone
import typer, numpy as np
from .features.build import build_features
from src.cdp.db import get_con


app = typer.Typer(help="CDP Sandbox CLI")


def _rid(n=12):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))


@app.command("seed")
def seed(users: int = 1000, days: int = 90, seed: int = 42):
    """Generate synthetic events and load into DuckDB."""
    rng = np.random.default_rng(seed)
    con = get_con()
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

    rows = []

    # ✅ anchor at "now - (days-1)" so data spans up to *today*
    start = datetime.now(timezone.utc) - timedelta(days=days - 1)

    for i in range(users):
        user_id = f"user_{i:05d}"
        anonymous_id = None
        base_rate = rng.uniform(0.2, 1.5)
        purchase_chance = rng.uniform(0.01, 0.15)

        for d in range(days):
            # ✅ spread events across the full window using the loop index
            t = start + timedelta(
                days=d,
                hours=int(rng.integers(0, 24)),
                minutes=int(rng.integers(0, 60))
            )

            # page views
            for _ in range(rng.poisson(base_rate)):
                rows.append([_rid(), user_id, anonymous_id, "page", "{}", t])

            # add_to_cart (and maybe purchase)
            if rng.random() < min(0.3, base_rate / 3):
                rows.append([_rid(), user_id, anonymous_id, "add_to_cart", "{}", t])
                if rng.random() < purchase_chance:
                    amount = float(np.round(rng.uniform(10, 120), 2))
                    rows.append([_rid(), user_id, anonymous_id, "purchase", f'{{"amount": {amount}}}', t])

            # occasional session_start
            if rng.random() < 0.3:
                rows.append([_rid(), user_id, anonymous_id, "session_start", "{}", t])

    df = pd.DataFrame(rows, columns=["event_id","user_id","anonymous_id","event","properties","ts"])
    con.register("tmp_df", df)
    con.execute("INSERT INTO events SELECT * FROM tmp_df")
    typer.echo(f"Seeded {len(df):,} events for {users} users over {days} days.")

@app.command("score-propensity")
def score_model():
    import joblib, pandas as pd
    from src.cdp.db import get_con
    
    con = get_con()
    df = con.sql("SELECT * FROM features_daily").fetchdf()
        
    X = df.drop(columns=["user_id","y"]).fillna(0.0)
    model = joblib.load("data/artifacts/propensity_30d.joblib")
    df["score"] = model.predict_proba(X)[:,1]
    
    con.register("tmp_scores", df[["user_id","score"]])
    con.execute("CREATE OR REPLACE TABLE propensity_scores AS SELECT * FROM tmp_scores")
    print("Propensity scores written to DuckDB table `propensity_scores`.")


@app.command("features-build")
def features_build():
    build_features()
    typer.echo("features_daily built.")

@app.command("train-propensity")
def train_model():
    from src.cdp.ml.train_propensity import train as train_propensity
    info = train_propensity()
    typer.echo(f"Trained propensity model. Report: {info['report_path']}" )

if __name__ == "__main__":
    app()


