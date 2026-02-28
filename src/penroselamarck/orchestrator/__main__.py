"""Exercise orchestrator runtime bootstrap."""

from __future__ import annotations

import json
import logging
import os

from penroselamarck.orchestrator.exercise_orchestrator import (
    ExerciseOrchestrator,
    ExerciseOrchestratorSettings,
)
from penroselamarck.orchestrator.observability import configure_observability
from penroselamarck.services.container import ServiceContainer

_LOGGER = logging.getLogger("penroselamarck.orchestrator")


def main() -> int:
    _configure_logging()
    telemetry = configure_observability()
    settings = ExerciseOrchestratorSettings.from_env()
    orchestrator = ExerciseOrchestrator(services=ServiceContainer(), telemetry=telemetry)
    result = orchestrator.run_once(settings)
    _LOGGER.info("orchestrator run completed: %s", json.dumps(result, sort_keys=True))
    return 0


def _configure_logging() -> None:
    level_name = os.environ.get("LOG_LEVEL", "INFO").strip().upper() or "INFO"
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


if __name__ == "__main__":
    raise SystemExit(main())
