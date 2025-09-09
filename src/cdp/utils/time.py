from datetime import datetime, timezone, timedelta

def now_utc():
    return datetime.now(timezone.utc)

def days_ago(n):
    return now_utc() - timedelta(days=n)
