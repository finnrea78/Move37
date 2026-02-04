"""
OpenLineage helpers for Penrose-Lamarck.

Emits lineage events to a configured Marquez endpoint.

Public API
----------
- :func:`emit_openlineage_run`: Emit a start and complete run event.

Attributes
----------
DEFAULT_NAMESPACE : str
    Default namespace for lineage events.

Examples
--------
>>> from penroselamarck.db.lineage import emit_openlineage_run
>>> emit_openlineage_run("seed", {"seed": 1}, ["inputs"], ["outputs"])

See Also
--------
:mod:`penroselamarck.db.bin.seed`
"""

from __future__ import annotations

import os
import sys
from collections.abc import Iterable
from datetime import datetime, timezone

try:
    from openlineage.client import OpenLineageClient
    from openlineage.client.run import InputDataset, Job, OutputDataset, Run, RunEvent, RunState
    from openlineage.client.transport.http import HttpTransport
    from openlineage.client.uuid import generate_new_uuid
except Exception:  # pragma: no cover - import guard
    OpenLineageClient = None  # type: ignore[assignment]
    Job = None  # type: ignore[assignment]
    Run = None  # type: ignore[assignment]
    RunEvent = None  # type: ignore[assignment]
    RunState = None  # type: ignore[assignment]
    HttpTransport = None  # type: ignore[assignment]
    generate_new_uuid = None  # type: ignore[assignment]
    InputDataset = None  # type: ignore[assignment]
    OutputDataset = None  # type: ignore[assignment]

DEFAULT_NAMESPACE = "penroselamarck"


def emit_openlineage_run(
    job_name: str,
    run_args: dict[str, str | int | float],
    inputs: Iterable[str],
    outputs: Iterable[str],
    namespace: str | None = None,
) -> None:
    """
    emit_openlineage_run(job_name, run_args, inputs, outputs, namespace=None) -> None

    Concise (one-line) description of the function.

    Parameters
    ----------
    job_name : str
        Logical job name for lineage tracking.
    run_args : Dict[str, str | int | float]
        Run arguments stored as run facets.
    inputs : Iterable[str]
        Input dataset identifiers.
    outputs : Iterable[str]
        Output dataset identifiers.
    namespace : Optional[str]
        Namespace override for dataset and job events.

    Returns
    -------
    None
        Emits OpenLineage run events when configured.

    Examples
    --------
    >>> callable(emit_openlineage_run)
    True
    """
    url = os.getenv("OPENLINEAGE_URL")
    if not url:
        return
    if (
        OpenLineageClient is None
        or InputDataset is None
        or OutputDataset is None
        or generate_new_uuid is None
    ):
        print("[lineage] OpenLineage client unavailable", file=sys.stderr)
        return

    ns = namespace or os.getenv("OPENLINEAGE_NAMESPACE", DEFAULT_NAMESPACE)
    try:
        transport = HttpTransport(url=url)
        client = OpenLineageClient(transport=transport)
        run_id = generate_new_uuid()
        job = Job(namespace=ns, name=job_name)
        run = Run(runId=run_id)
        input_datasets = [InputDataset(namespace=ns, name=name) for name in inputs]
        output_datasets = [OutputDataset(namespace=ns, name=name) for name in outputs]
        started = RunEvent(
            eventType=RunState.START,
            eventTime=datetime.now(timezone.utc).isoformat(),
            run=run,
            job=job,
            inputs=input_datasets,
            outputs=output_datasets,
            runFacets={"runArgs": {"_producer": "seed", "args": run_args}},
        )
        completed = RunEvent(
            eventType=RunState.COMPLETE,
            eventTime=datetime.now(timezone.utc).isoformat(),
            run=run,
            job=job,
            inputs=input_datasets,
            outputs=output_datasets,
            runFacets={"runArgs": {"_producer": "seed", "args": run_args}},
        )
        client.emit(started)
        client.emit(completed)
    except Exception as exc:  # pragma: no cover - defensive logging
        print(f"[lineage] Emit failed: {exc}", file=sys.stderr)
