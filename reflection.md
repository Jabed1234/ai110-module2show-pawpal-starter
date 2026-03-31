# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

1. User

- Name
- Username
- List of pets
- addPet()
- removePet()
- viewPets()
- viewTasks()

2. Pet

- pet name
- tasks
- addTask()
- removeTask()
- getTasks()

3. task

- task type
- task time
- taskStatus
- markComplete()
- editTask()
- deleteTask()

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes. After implementing the dataclass skeletons in `pawpal_system.py` I made a few small, concrete changes to make the system usable for simple operations and to avoid immediate logical bottlenecks:

- Implemented basic method bodies for `Task`, `Pet`, and `User` instead of leaving them as stubs. Why: leaving all methods unimplemented meant the classes were not yet testable or useful; small, explicit implementations make it possible to run simple unit tests and iterate on behavior.

- Task behavior: `mark_complete()` now sets `task_status = 'completed'`; `edit_task()` updates only supplied fields; `delete_task()` is implemented as a soft-delete by setting `task_status = 'deleted'`. Why: Soft-deletes avoid surprising side-effects when a Task instance is referenced elsewhere (for example, in historical logs) and makes removal an explicit container operation (Pet/User).

- Pet behavior: `add_task()` appends to the pet's task list, `remove_task()` removes (and raises if missing), and `get_tasks()` returns a shallow copy. Why: This keeps container semantics simple and predictable while surfacing misuse (attempting to remove a non-existent task) early during development.

- User behavior: `add_pet()`/`remove_pet()` append/remove pets, `view_pets()` returns a copy of the pets list, and `view_tasks()` flattens tasks from all owned pets. Why: Flattening tasks on the User simplifies client code that needs a user's full task view.

These changes prioritise testability and predictable container semantics. Next iterations could add duplicate checks, IDs for entities, persistence hooks (to/from dict or JSON), and more sophisticated delete/restore policies.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff the scheduler currently makes is that conflict detection checks only for exact datetime matches rather than overlapping time intervals (durations). That is, two tasks that overlap partially but do not share the exact same start time will not be flagged as a conflict.

Why this is reasonable: checking only for exact matches keeps conflict detection lightweight and cheap to compute (O(n) grouping by timestamp) and is adequate for a simple MVP where tasks are usually scheduled on precise times (e.g., "8:00 walk"). For richer scheduling (tasks with durations and fuzzy overlaps) the scheduler would need interval arithmetic and more expensive checks; that complexity is appropriate in a later iteration once task durations, priorities, and rescheduling policies are fully specified.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI (VS Code Copilot and Copilot Chat) throughout the project as a pair-programming assistant across several, focused phases:

- Design brainstorm: I asked Copilot Chat to help translate my UML notes into concrete Python class sketches and to suggest method names and signatures.
- Rapid implementation: I relied on inline Copilot completions to expand small method bodies (sorting, filtering, next-occurrence logic) and to suggest idiomatic Python patterns (sorted with a key lambda, timedelta arithmetic).
- Tests & verification: I used the Generate tests smart actions and Copilot Chat to draft pytest tests (sorting, recurrence, conflict detection) and iterated until they passed.
- Docs and UX: I used Copilot to draft short docstrings, README snippets, and commit messages so the repo stayed documented and the commits were meaningful.

The most helpful prompts were small, concrete requests ("give me a function that sorts Task objects by their datetime using sorted(..., key=...)"), or task-focused multi-step prompts ("produce a pytest that marks a daily task complete and checks the next occurrence is tomorrow"). Short, precise requests for code snippets plus examples of expected input/output produced the best results.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

One clear example: an early suggestion from Copilot Chat (and some inline completions) encouraged letting a Task remove itself from its container (Pet) when deleted. I rejected that because it creates surprising side-effects and ambiguous ownership of objects. Instead I implemented a soft-delete on Task (status='deleted') and kept add/remove responsibilities with the container (Pet/Owner). That decision keeps object ownership explicit, simplifies reasoning about references, and makes persistence/undo easier.

How I verified/validated AI suggestions:

- Write a small, focused test that captures the intended behavior (unit tests for Task deletion and Pet.remove_task).
- Run the CLI demo and Streamlit UI to observe real interactions (ensured soft-deleted tasks do not disappear unexpectedly and that removal raises when appropriate).
- Prefer explicit, simple implementations over clever-but-implicit shortcuts; if AI suggested a concise one-liner that hid important behavior, I rewrote it to be explicit and testable.

Using separate chat sessions for each phase (design, implementation, UI, testing) helped keep conversations scoped and the suggestions relevant. Each session held only the context needed for that phase, which reduced confusion, made it easier to find useful snippets later, and matched the development workflow (design → build → test → integrate).

Key lessons about being the "lead architect" while collaborating with AI:

- Define clear interfaces and ownership early (who owns tasks? which component mutates lists?). These constraints guide the AI toward safer suggestions.
- Keep the AI in the loop for boilerplate and options, but retain final design decisions—reject suggestions that violate invariants or add hidden side-effects.
- Always codify expectations into tests immediately; tests are the best way to turn a suggestion into a verified design.
- Prefer small, incremental changes. Use the AI to propose variants, but choose the simplest, most maintainable option and document the tradeoffs.
- Use Chat sessions as disposable brainstorming spaces, and move the accepted solutions into the codebase with tests and docs.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I wrote and ran an automated pytest suite that verifies the core behaviors of the logic layer. The tests cover:

- Basic Task and Pet behavior: creating tasks, adding tasks to a Pet, and ensuring removal semantics are correct. These validate the container/ownership model and basic CRUD-like operations.
- Task completion: verifying that calling `mark_complete()` sets the task status to `completed` and records a completion timestamp. This ensures state transitions are correct.
- Sorting correctness: `Scheduler.sort_by_time()` returns tasks in chronological order even when tasks are added out of order. Correct ordering is fundamental for any schedule display.
- Recurrence logic: marking a daily task complete returns/creates a next occurrence with the correct date (today + 1 day). This verifies the simple recurrence automation works.
- Conflict detection: `Scheduler.detect_conflicts()` flags tasks scheduled at the exact same datetime across pets. This confirms the lightweight conflict detector triggers when expected.

These tests are important because they exercise the scheduler's primary responsibilities (tracking, ordering, recurring behavior, and surface-level conflict detection) and they provide a safety net for future refactors.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

Confidence level: High for the implemented behaviors (4/5). The unit tests are green and the small CLI and Streamlit demos exercise common flows.

Key edge cases and next tests I would add:

- Overlapping-duration conflicts: currently conflicts are only detected for exact start-time matches; I would add tasks with durations and test interval-overlap detection and resolution.
- Timezones and DST: ensure scheduled datetimes behave correctly when owner/local timezone differs from server timezone.
- Persistence and recovery: serialize Owner/pet/task state to JSON and restore it, then verify no information is lost.
- Concurrency / multi-user safety: if the app were used by multiple clients, test for race conditions in state updates.
- Validation and duplicates: test duplicate task prevention (same pet, same time/title) and behavior for invalid inputs.

Addressing these would raise confidence toward 5/5.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

What went well:

- Design-first workflow: drafting the UML and converting it into dataclasses gave a clear contract for the rest of the work.
- Incremental development and testing: small, focused unit tests made it easy to validate each feature as I added it.
- Clean separation of concerns: `pawpal_system.py` (logic) and `app.py` (UI) remain decoupled; Scheduler is stateless and operates on Owner instances, which simplified testing and UI wiring.
- Productive AI collaboration: Copilot speeded up boilerplate and suggested idiomatic code patterns while tests and design constraints ensured correctness.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

What I'd improve next:

- Add stable IDs for Owner/Pet/Task and implement persistent storage (JSON or a lightweight DB) so the app survives server restarts.
- Implement interval-aware conflict detection and a simple automatic resolver (suggest alternate times based on owner availability).
- Expand recurrence rules (support N-day intervals, weekly on specific weekdays, and exceptions) and surface them in the UI.
- Add form validation, duplicate checks, and clearer UX for editing/removing tasks.
- Add CI (GitHub Actions) to run tests and linting on each push.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Key takeaway:

AI (Copilot) is a powerful productivity partner for implementation and brainstorming, but it works best when guided by a clear architecture, concise interfaces, and tests. As the lead architect you still need to set invariants (ownership, mutability, side-effect policies), convert AI suggestions into explicit, testable code, and prefer readability and predictability over clever brevity. Tests are the ultimate arbiter: they turn design intent and AI suggestions into verified behavior.
