"""Structured logging of the core service: one JSON object per line on stdout (docs/06 D1.7)."""

import json
import logging
import logging.config
from contextvars import ContextVar
from datetime import UTC, datetime

# Id of the request being handled. Each request runs in its own context, so
# concurrent requests never see each other's id. None outside of a request.
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


class JsonFormatter(logging.Formatter):
    """Turn each log record into one line of JSON that a machine can search and filter."""

    def format(self, record: logging.LogRecord) -> str:
        """Build the JSON line: common fields, the record's extra fields and any exception."""
        entry = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
        }
        entry.update(getattr(record, "fields", {}))
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, ensure_ascii=False)


def configure_logging() -> None:
    """Send all logs, including Uvicorn's, to stdout as JSON.

    Docker collects stdout, so the service never writes log files. Uvicorn's
    access log is silenced because the request middleware in core.main replaces
    it: that one includes the request id and leaves out the query string.
    """
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"json": {"()": JsonFormatter}},
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "json",
                },
            },
            "root": {"level": "INFO", "handlers": ["stdout"]},
            "loggers": {
                "uvicorn": {"handlers": [], "propagate": True},
                "uvicorn.error": {"handlers": [], "propagate": True},
                "uvicorn.access": {"handlers": [], "propagate": False, "level": "CRITICAL"},
            },
        }
    )
