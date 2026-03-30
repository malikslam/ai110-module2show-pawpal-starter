# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The scheduler goes beyond a simple task list with four algorithmic improvements:

- **Chronological sorting** — `Scheduler.sort_by_time()` reorders any task list by actual start time using `datetime` parsing, so output always reads top-to-bottom regardless of input order.
- **Status and pet filtering** — `DailyPlan.pending()` and `DailyPlan.completed_tasks()` let you query what's left or done. `Scheduler.filter_by_pet()` isolates tasks by pet name for multi-pet households.
- **Recurring task auto-scheduling** — When `Scheduler.mark_task_complete()` is called, it automatically creates the next occurrence via `Task.next_occurrence()`, advancing `due_date` by 1 day (daily) or 7 days (weekly) using `timedelta`.
- **Conflict detection** — `Scheduler.detect_conflicts()` scans one or more pets' plans for overlapping time windows within each slot (morning / midday / evening) and returns human-readable warnings without crashing the program.

## Testing PawPal+

### Run the tests

```bash
python -m pytest test_pawpal.py -v
```

### What the tests cover

| Category | Tests |
|---|---|
| **Task status** | `mark_complete()` flips `completed` to `True`; adding tasks increases pet task count |
| **Sorting** | Tasks added out of order are returned chronologically; single-task and empty-list edge cases handled without error |
| **Recurrence** | Daily task produces a next occurrence due tomorrow; weekly task due in 7 days; month/year rollover (e.g. March 31 → April 1) works correctly |
| **Auto-scheduling** | `Scheduler.mark_task_complete()` appends the next occurrence to `pet.tasks` with `completed=False` |
| **Conflict detection** | Overlapping tasks in the same slot produce a warning; tasks in different slots do not; exact same start time is flagged |

### Confidence Level

⭐⭐⭐⭐ (4/5)

The core scheduling logic — priority ordering, time slot assignment, recurrence, and conflict detection — is well covered by 12 passing tests including edge cases like month rollover and identical start times. One star is held back because the Streamlit UI layer (`app.py`) has no automated tests; session state behavior and form interactions are only verified manually.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
