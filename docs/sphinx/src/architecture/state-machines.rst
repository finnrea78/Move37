Workflow State Machines
=======================

These diagrams describe the intended behavior of the current product workflows
independent of client: REST, MCP, CLI, or web.

Training Session
----------------

.. mermaid::

   stateDiagram-v2
       [*] --> SessionRequested
       SessionRequested --> SessionCreated: practice.start
       SessionCreated --> ExerciseBatchPrepared: select exercises
       ExerciseBatchPrepared --> AwaitingAnswer: practice.next
       AwaitingAnswer --> AnswerSubmitted: practice.submit
       AnswerSubmitted --> AnswerScored: evaluate answer
       AnswerScored --> AttemptRecorded: persist attempt
       AttemptRecorded --> AwaitingAnswer: exercises remain
       AttemptRecorded --> SessionCompleted: no exercises remain
       SessionCompleted --> SessionClosed: practice.end or implicit completion
       SessionClosed --> [*]

       SessionRequested --> SessionFailed: invalid request
       AwaitingAnswer --> SessionFailed: unknown session or no remaining exercise
       AnswerSubmitted --> SessionFailed: unknown exercise or invalid session
       SessionFailed --> [*]

Exercise Ingestion
------------------

.. mermaid::

   stateDiagram-v2
       [*] --> RequestReceived
       RequestReceived --> PayloadNormalized: parse and normalize input
       PayloadNormalized --> DuplicateCheck: compute content hash
       DuplicateCheck --> PersistExercise: unique exercise
       DuplicateCheck --> DuplicateDetected: duplicate content
       PersistExercise --> PostPersistProcessing: infer classes / refresh graph/search views
       PostPersistProcessing --> Completed
       DuplicateDetected --> Completed

       PayloadNormalized --> Rejected: invalid payload
       PersistExercise --> Rejected: persistence failure
       PostPersistProcessing --> Rejected: processing failure
       Rejected --> [*]

Performance Assessment
----------------------

.. mermaid::

   stateDiagram-v2
       [*] --> ViewRequested
       ViewRequested --> FiltersResolved: parse filters
       FiltersResolved --> MetricsQueried: aggregate attempts
       MetricsQueried --> DataAvailable: metrics found
       MetricsQueried --> EmptyState: no attempts yet
       DataAvailable --> Completed
       EmptyState --> Completed

       FiltersResolved --> Failed: invalid filters
       MetricsQueried --> Failed: query failure
       Failed --> [*]
