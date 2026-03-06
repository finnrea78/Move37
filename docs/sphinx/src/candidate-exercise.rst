Candidate Exercise
==================

Penrose-Lamarck is used as part of Roche engineering hiring. Candidates work in
the real repository, solve one or more GitHub issues, and submit a pull request
from their own fork.

What Candidates Must Do
-----------------------

- Create an anonymous GitHub account for the submission.
- Fork this repository from that account.
- Pick one or more GitHub issues and implement a solution.
- Open a pull request from the fork against this repository.
- Follow the repository pull request template.
- Keep the exercise to about one hour of focused work.
- Submit within seven days of receiving the invitation.
- Use the issue acceptance criteria as the target behavior, but prioritize a
  clear pull request with prompt history, validation evidence, and honest notes
  about what was or was not completed.

What We Look For In A Pull Request
----------------------------------

- A working solution for the selected issue or issues.
- Clear evidence that the change was validated.
- A prompt history showing how the coding assistant was used to explore and
  solve the task.
- Notes on assistant mistakes, incomplete suggestions, or misleading
  suggestions, and how they were corrected.
- Any limitations, deferred work, edge cases, or improvements the candidate
  noticed but chose not to address.

Evaluation Priority
-------------------

Meeting the acceptance criteria of the issue is useful, but it is not the only
signal and it is not always the most important one.

If a candidate starts from an issue, whether suggested by the repository or
created during the work, we care at least as much about:

- the prompt history and how the coding assistant was directed
- the candidate's ability to validate and question the proposed solution
- mistakes or weak suggestions from the assistant and how they were handled
- honest reporting of incomplete behavior, limitations, and follow-up work

A partially complete solution with strong evidence of reasoning, validation, and
assistant supervision is more valuable than an apparently complete solution that
lacks that evidence.

Changing Direction
------------------

Candidates are allowed to change direction if, while working on an issue, they
discover that another problem in the repository is broken, blocks progress, or
is more important to fix.

This includes functionality that exists in the project but may not be fully
working yet, such as observability, developer tooling, or local runtime
behavior.

The repository is a work in progress, so candidates may also encounter
unfinished or partially tested areas such as EKS deployment, observability
coverage, or other supporting infrastructure. Those areas are valid routes if
the candidate judges them worth addressing and can satisfy the dependencies
needed to work on them responsibly.

If you do this:

- explain which issue you started from
- explain what you discovered
- explain why you changed direction
- explain why the final scope was the better use of time

Choosing a smaller issue is allowed, but part of the exercise is demonstrating
judgment about what is worth fixing within the available time.

Prompt History
--------------

The pull request template asks candidates to include the significant prompts and
exploratory questions that shaped the work.

- Include prompts only, not assistant responses.
- Include exploratory questions when they materially helped build context.
- If an assistant response was wrong in an important way, describe it in the
  ``AI Mistakes And Corrections`` section of the pull request instead.

Typical Follow-Up Questions
---------------------------

If a pull request is merged and the proposed solution is running, follow-up
questions may include:

- Why did the agent propose that solution?
- What did you disagree with in the assistant's suggestions?
- Did the assistant introduce new dependencies, patterns, or design choices?
- If so, what trade-off analysis did you do before accepting them?
- How did you convince yourself that the solution was correct?
- What would you improve next if you had more time?
