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

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
