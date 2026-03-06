Data Model
==========

Penrose-Lamarck is practice-first. The core schema stores exercises, practice
sessions, learner attempts, and derived performance aggregates.

Resource URIs
-------------

The schema includes optional ``uri`` columns for stable external identifiers.
The intended convention is:

- Namespace: ``pluid``
- Format: ``<namespace>:<entity>:<hash>``
- Example: ``pluid:exercise:6ee4c2db8c24e4d9``

Core Tables
-----------

``exercises``
   Canonical exercise bank. Stores question, answer, language, tags, classes,
   content hash, timestamps, and an optional URI.

``practice_sessions``
   Stores one learner session with language, selection strategy, target count,
   lifecycle status, timestamps, and the selected exercise queue.

``attempts``
   Append-only learner submissions recorded against one exercise inside one
   practice session, including score, pass flag, and evaluation timestamp.

``performance_summaries``
   Schema-level derived aggregates per exercise. The table exists for
   denormalized metrics, although the current metrics implementation still
   computes aggregates directly from ``attempts``.

Integrity Rules
---------------

- ``attempts.session_id`` references ``practice_sessions.session_id``.
- ``attempts.exercise_id`` references ``exercises.id``.
- ``performance_summaries.exercise_id`` references ``exercises.id``.
- ``exercises.content_hash`` is unique and is used for deduplication.
- ``exercises.language``, ``exercises.content_hash``, ``attempts.session_id``,
  and ``attempts.exercise_id`` are indexed for retrieval and aggregation flows.

End-To-End Example
------------------

.. code-block:: json

   {
     "exercise": {
       "id": "ex_da_001",
       "language": "da",
       "content_hash": "9b4d6f95d5c3f5c7f6c2a11f86a88f4f86f9d4a2f730f6b73d0be02c1ee11e0d"
     },
     "practice_session": {
       "session_id": "sess_20260227_0001",
       "language": "da",
       "strategy": "mixed",
       "target_count": 5,
       "status": "ended"
     },
     "attempt": {
       "id": "att_20260227_00042",
       "session_id": "sess_20260227_0001",
       "exercise_id": "ex_da_001",
       "score": 1.0,
       "passed": true
     },
     "performance_summary": {
       "exercise_id": "ex_da_001",
       "total_attempts": 12,
       "pass_rate": 0.83
     }
   }
