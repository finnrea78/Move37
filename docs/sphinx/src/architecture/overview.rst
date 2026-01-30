Overview
========

Penrose-Lamarck is a learning platform designed to preserve human cognitive
sovereignty in the age of AI. The architecture prioritizes:

- Clean separation of domain logic from infrastructure (Clean Architecture).
- GenAI orchestration with explicit tool boundaries via MCP servers.
- Retrieval-augmented generation for verifiable reasoning.
- Continuous evaluation, observability, and governance.

Core Principles
---------------

- **Domain isolation:** The learning domain is framework-agnostic.
- **Ports and adapters:** All I/O is abstracted by interfaces.
- **Immutable state:** Domain data is treated as immutable by default.
- **Safety and traceability:** Every model response is evaluated, traced, and
  attributable to a source.

Container Runtime
-----------------

The platform standardizes on **Podman** for containerization:

- Daemonless design improves security and auditability.
- Rootless-first execution aligns with least-privilege standards.
- Strong OCI compliance and systemd integration fit enterprise operations.

Nerdctl is a strong alternative in containerd-native environments, but Podman
provides more secure defaults for multi-service developer and CI workloads.
