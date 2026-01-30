GenAI Orchestration
===================

LangGraph Workflow
------------------

LangGraph coordinates multi-step workflows with explicit state transitions:

1. Ingest source content.
2. Chunk and embed documents.
3. Index into vector and graph stores.
4. Retrieve evidence for a query.
5. Generate structured reasoning traces.
6. Evaluate and score the output.

MCP Tooling
-----------

All external tools are exposed through Model Context Protocol (MCP) servers.
This enforces strict tool boundaries and improves auditability.

Recommended MCP services:

- `mcp-llm`: model gateway and routing.
- `mcp-retrieval`: hybrid search and re-ranking.
- `mcp-docs`: ingestion and document validation.
- `mcp-tools`: bioinformatics, code execution, math.

Agent Protocol
--------------

Agents follow a shared protocol:

- Explicit tool calls with typed inputs/outputs.
- Observable state transitions.
- Safety and policy checks at each step.
