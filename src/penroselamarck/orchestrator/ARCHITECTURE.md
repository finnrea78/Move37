# Orchestrator Architecture Guide

This document explains the internal architecture of `penroselamarck.orchestrator`, why the package is structured this way, and where to add new capabilities.

## 1. Core Principles

1. Dependency inversion: workflow logic depends on interfaces (`ports`), not concrete vendors.
2. Prompt/data separation: prompts are versioned files, not hard-coded strings.
3. Replaceable providers: OpenAI is one provider implementation, not the orchestrator itself.
4. Explicit boundaries: GitHub crawling, persistence, LLM calls, and workflow engines are separate concerns.

## 2. Package Layers

### `models/`
Runtime dataclasses for orchestrator state and step I/O.

- `core.py`: repository target and candidate payloads.
- `workflow.py`: thresholds, retry policy, per-item and run summaries.

These are **not** SQLAlchemy table models.

### `ports/`
Provider-neutral interfaces.

- `steps.py`: `Extractor`, `Classifier`, `Scorer`, `TransientStepError`.
- `storage.py`: `WorkflowStore`.
- `research.py`: online-research extension point for agentic flows.
- `tools.py`: tool-runtime extension point for agent/tool execution.

### `prompts/`
Versioned prompt assets and rendering infrastructure.

- `templates/<step>/<version>/system.txt`
- `templates/<step>/<version>/user.txt`
- `templates/<step>/<version>/schema.json`
- `registry.py`: prompt loading/version selection.
- `renderer.py`: runtime variable substitution.

### `providers/`
Concrete adapters that implement ports.

- `providers/llm/openai/`: OpenAI extractor/classifier/scorer.

### Existing adapters and engines

- `github_crawler.py`: GitHub API + repository reader.
- `sql_store.py`: SQLAlchemy persistence adapter.
- `langgraph_workflow.py`: graph-based workflow engine.
- `workflow.py`: sequential workflow engine.
- `observability.py`: OTel metrics and tracing.

## 3. Prompt Versioning Strategy

Prompt versions can be rolled independently by step:

- `ORCHESTRATOR_PROMPT_VERSION` (global fallback)
- `ORCHESTRATOR_EXTRACTION_PROMPT_VERSION`
- `ORCHESTRATOR_CLASSIFICATION_PROMPT_VERSION`
- `ORCHESTRATOR_SCORING_PROMPT_VERSION`

This enables controlled experimentation and targeted prompt updates without changing provider code.

## 4. Adding a New LLM Provider

1. Create a package under `providers/llm/<provider_name>/`.
2. Implement classes that satisfy `Extractor`, `Classifier`, and `Scorer` ports.
3. Reuse prompt registry/renderer unless provider requires specialized formatting.
4. Wire the provider in bootstrap/runtime (`__main__.py` or a future factory module).

## 5. Preparing for Agentic Workloads

The architecture already includes explicit ports for:

- online research (`ResearchClient`)
- tool runtime (`ToolRuntime`)

Future workflow nodes can consume these ports while keeping engine code and providers decoupled.

## 6. Backward Compatibility

- `contracts.py` remains as a compatibility facade over `ports/`.
- `openai_steps.py` remains as a compatibility re-export of OpenAI provider classes.

New code should import from `ports/` and `providers/` directly.
