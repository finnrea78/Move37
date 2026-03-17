"""Structured logging helpers for RAG runtime and worker."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


def configure_logging() -> logging.Logger:
    """Return a stdout logger for container log shipping."""

    logger = logging.getLogger("move37-rag")
    if logger.handlers:
        return logger
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def log_event(logger: logging.Logger, **payload: Any) -> None:
    """Emit a structured JSON log line."""

    logger.info(
        json.dumps(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                **payload,
            },
            default=str,
        )
    )
