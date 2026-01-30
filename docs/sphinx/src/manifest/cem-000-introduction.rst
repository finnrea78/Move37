Introduction and Purpose (CEM-000)
==================================

This document specifies the technical requirements and structure for the
Catalyx Engineering Manifest (CEM), a foundational set of recommendations and
guidelines for software development within the team. The CEM aims to enforce
consistency, promote best practices, accelerate development via reusable
blueprints, and formalize the expression of business intent using state
machines for Outcome Driven Development (ODD).

Emphasis
--------

- **Unique Identifiers:** Every recommendation must be referable via a unique ID, ensuring traceability.
- **Versioning:** Recommendations are individually versioned, allowing for controlled, incremental refinement.
- **Actionable Blueprints:** Prescriptive guidance is paired with "zero-effort" code repositories to minimize friction in adoption.
- **Formal Intent Language:** Business outcomes are modeled using a machine-readable state machine language.

Getting Started (CEM-000-000)  
-------------------------------------------

The rule unique IDs must be used to back any decision based on a formal
guideline, e.g.:

- PR reviews
- Git-hooks
- Choosing a database for vector stores

The appropriate rule won't always exist a priori in the manifest; the document
is a continuous WIP. The appropriate rule may exist but require refinement to
adapt to the current use case. In any case, refer to ``CEM-000-001``.

Contributing (CEM-000-001)  
----------------------------------------

To add or refine a rule, follow ``CEM-001-000``

.. warning::
   Maintenance Overhead

   To prevent maintenance overhead, use existing refinement sessions or other
   team meetings to refine the manifest. For example, during an architecture
   review where Redis is chosen over DynamoDB, upgrade the manifest immediately.

.. note::
   Recommendations are Specifications, not Rules

   You are expected to follow recommendations but encouraged to find new ways
   of implementing them, provided you document your choice and inform the team.

Examples
--------

A great example of a fine contribution:

.. code-block:: text

   "I want to use nerdctl rather than podman. It satisfies the container hosting
   specifications laid out by the team (TODO), so I'll add nerdctl to the
   specification and ask for feedback."

A less great example:

.. code-block:: text

   "I couldn't be bothered with contributing. Docker has always been my thing.
   I'll tackle any consequent issues as they come. It's nobody's business what I
   use."

Glossary (CEM-000-003)  
------------------------------------

.. list-table:: Glossary of Terms
   :widths: 15 25 45 15
   :header-rows: 1

   * - ID
     - Term
     - Semantics
     - Example
   * - GT1
     - Artifacts of Intent
     - A functional outcome, a behaviour, as opposed to the implementation of the outcome or behaviour
     - CEM-004-000

Bibliography (CEM-000-004)  
----------------------------------------

Add resources of interest below, whether or not they are referenced in the manifest.

.. list-table:: Bibliography
   :widths: 15 35 50
   :header-rows: 1

   * - ID
     - Resource
     - Semantics
   * - R1
     - Code Guidelines
     - Karpathy inspired Claude code guidelines
