Evaluation Framework
====================

Goals
-----

- Measure retrieval quality, faithfulness, and reasoning consistency.
- Prevent regression via automated eval gates.

Tooling
-------

- **RAGAS:** RAG faithfulness and answer relevance.
- **TruLens** or **DeepEval:** model evaluation and rubric scoring.
- **Promptfoo:** prompt regression and scenario testing.

Evaluation Flow
---------------

1. Run batch evaluation against golden datasets.
2. Gate deployments on thresholds.
3. Log metrics to observability stack for trend analysis.
