"""Entry point of the core service: creates the FastAPI app and its routes."""

import logging
from typing import Annotated

from fastapi import Depends, FastAPI, Response, status
from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

from core.db import get_engine

logger = logging.getLogger(__name__)

app = FastAPI(title="core")


@app.get("/health")
def health() -> dict[str, str]:
    """Report that the service process is alive.

    Used by Docker health checks, the gateway and the external monitor.
    It does not check the database; that is `/health/ready` (docs/06 D1.2).
    """
    return {"status": "ok"}


@app.get(
    "/health/ready",
    responses={503: {"description": "The database is not reachable"}},
)
def health_ready(
    engine: Annotated[Engine, Depends(get_engine)], response: Response
) -> dict[str, str]:
    """Report that the service can serve requests: alive AND able to query its database.

    Used by the Compose health check and the external monitor (docs/06 D1.2).
    On failure it answers 503 with no internal details (docs/06 D1.10, A10);
    the cause is written to the log instead.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.exception("Readiness check failed: database not reachable")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unavailable"}
    return {"status": "ok"}
