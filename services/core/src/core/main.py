"""Entry point of the core service: creates the FastAPI app and its routes."""

from fastapi import FastAPI

app = FastAPI(title="core")


@app.get("/health")
def health() -> dict[str, str]:
    """Report that the service process is alive.

    Used by Docker health checks, the gateway and the external monitor.
    It does not check the database; that is `/health/ready` (docs/06 D1.2).
    """
    return {"status": "ok"}
