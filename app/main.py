from fastapi import FastAPI
import structlog
from app.core.logging import configure_logging

configure_logging()
structlog.get_logger(__name__).info("boot_check")

app = FastAPI(title="fastapi-langgraph-agent")

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}