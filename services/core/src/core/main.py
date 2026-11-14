"""Entry point of the core service: creates the FastAPI app and its routes."""

import logging
from collections.abc import Awaitable, Callable
from time import perf_counter
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, Request, Response, status
from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

from core.db import get_engine
from core.logging_config import configure_logging, request_id_var

configure_logging()
logger = logging.getLogger(__name__)
access_logger = logging.getLogger("core.access")

app = FastAPI(title="core")


@app.middleware("http")
async def log_requests(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Log every request as one JSON line, tagged with its request id.

    Takes the id from the gateway's X-Request-ID header, or creates one when
    there is no gateway. Only the path is logged: never the query string,
    headers or body, which can hold tokens or personal data (docs/06 D1.7).
    Successful health checks go to DEBUG so they do not bury the rest.
    """
    request_id_var.set(request.headers.get("x-request-id") or str(uuid4()))
    start = perf_counter()
    status_code = 500  # Stays 500 if the endpoint raises an exception.
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        path = request.url.path
        app_path = path.removeprefix(request.scope.get("root_path", ""))
        is_quiet = app_path.startswith("/health") and status_code < 400
        access_logger.log(
            logging.DEBUG if is_quiet else logging.INFO,
            "request",
            extra={
                "fields": {
                    "method": request.method,
                    "path": path,
                    "status": status_code,
                    "duration_ms": round((perf_counter() - start) * 1000, 1),
                    "client_ip": request.client.host if request.client else None,
                }
            },
        )


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
