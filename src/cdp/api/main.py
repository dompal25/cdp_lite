from fastapi import FastAPI
from .routers import router

app = FastAPI(title="CDP Sandbox", version="0.1.0")
app.include_router(router, prefix="/v1")

@app.get("/")
def root():
    return {"ok": True, "service": "cdp-sandbox", "version": "0.1.0"}
