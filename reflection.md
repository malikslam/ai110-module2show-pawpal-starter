# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
    - The UML design consists of three classes: Pet, CareTask, and Scheduler. Pet holds the animal's basic info and preferences, CareTask represents a single care activity with a title, duration, and priority, and Scheduler takes both to produce an ordered daily plan. The design separates data from logic, with Scheduler depending on Pet and a list of CareTask objects to generate and explain the final schedule.

- What classes did you include, and what responsibilities did you assign to each?

About 7 classes will be needed to carry out implementation.

Owner
  - name, available_minutes_per_day
  - preferences (e.g., prefers morning walks, avoids late meds)

Pet 
- Which stores the pet's name, species, and care preferences
  - name, species, age, health_notes
  - owner: Owner

Task
- Which represents a single care activity with attributes for title, duration in minutes, and priority level (low, medium, or high)
  - title, duration_minutes
  - priority: "low" | "medium" | "high"
  - category: "walk" | "feeding" | "meds" | "grooming" | "enrichment"
  - time_of_day_constraint: Optional["morning" | "evening" | None]
  - frequency: "daily" | "weekly" (stretch goal)
  - is_required: bool  ← distinguishes critical vs. optional tasks

Scheduler
- It takes an owner name, a Pet instance, and a list of CareTask objects and produces an ordered daily care plan based on priority and time constraints
  - pet: Pet, tasks: List[Task], available_minutes: int
  - generate_plan() → DailyPlan

DailyPlan
- It collects the full ordered list of ScheduledTask objects for the day
  - scheduled: List[ScheduledTask]
  - skipped: List[Task]  ← tasks that didn't fit
  - explain() → str
  - total_time() → int

ScheduledTask
- It is a wrapper that links a Task to its place in the daily schedule — it holds the task itself, the assigned start_time (e.g. "8:00 AM"), and a reason string explaining why that task was chosen and placed at that time
  - task: Task
  - start_time: str (e.g. "8:00 AM")
  - reason: str  ← why this was chosen/placed here


**b. Design changes** 

- Did your design change during implementation?
 - Yes
- If yes, describe at least one change and why you made it.
 - Scheduler accepts available_minutes as a separate parameter instead of reading it from pet.owner.available_minutes_per_day — the Owner link is effectively unused
 - Owner.preferences and Pet.health_notes are stored but never consulted during scheduling, making them dead fields
 - ## ✅ Issues Fixed

All five identified issues have been resolved:

| Fix                                | What Changed                                                                                                                           |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **Owner link used**                | Scheduler now reads `pet.owner.available_minutes_per_day`, removing the redundant `available_minutes` parameter.                       |
| **No overlapping slots**           | Each slot (`morning`, `evening`, `None`) now maintains its own cursor via `slot_cursors`, which advances per task to prevent overlaps. |
| **TIME_SLOTS removed**             | Replaced with a `SLOT_STARTS` dictionary that is actively used to initialize slot cursors.                                             |
| **`frequency="weekly"` respected** | Tasks are filtered by `plan_weekday` before scheduling; daily tasks always pass.                                                       |
| **Priority validation**            | `Task.__post_init__` now raises a `ValueError` for invalid priority values instead of silently defaulting.                             |
| **Owner preferences used**         | `owner.preferences` are now appended to the `reason` field for each `ScheduledTask`.                                                   |
- Later updated the UML

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
### Constraints the scheduler considers

The scheduler follows a deterministic set of rules to ensure tasks are placed correctly and efficiently:

* **Required flag**
  Required tasks are always scheduled first, regardless of priority.

* **Priority**
  Tasks are ordered within required and optional groups by priority: **high → medium → low**.

* **Available time**
  Tasks that exceed the remaining available minutes for the day are skipped.

* **Time of day**
  Tasks constrained to `morning` or `evening` are scheduled within their designated slots.
  Tasks without a time constraint are scheduled starting from midday onward.

* **Frequency**
  Weekly tasks are only scheduled if their category matches `plan_weekday`.
  Daily tasks are always eligible.

- How did you decide which constraints mattered most?
- Required status ranks above priority because a missed medication is more critical than a missed play session. Time constraints come next since a morning walk at 6 PM defeats the purpose. Priority breaks ties among the remaining tasks, and available time acts as the final hard cutoff — no overscheduling.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
 - The scheduler uses a greedy first-fit approach — it picks tasks in priority order and schedules each one if it fits in the remaining time, without looking ahead to find a more optimal combination. 
- Why is that tradeoff reasonable for this scenario?
 - For a daily pet care plan, simplicity and predictability matter more than perfect optimization. An owner doesn't need the mathematically ideal schedule — they need a clear, explainable plan they can follow. A greedy approach also runs instantly and always produces the same output for the same input, which makes it easy to test and trust. The downside (occasionally skipping a shorter low-priority task to fit a longer one) is an acceptable tradeoff for a single-pet, single-day use case.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

AI tools were used across every phase of this project. During design, AI helped draft the initial UML class structure and identify missing relationships — for example, pointing out that `Owner` should link directly to `Scheduler` rather than passing `available_minutes` as a redundant parameter. During implementation, AI was used to debug logic bottlenecks such as the broken `frequency == category` weekly filter and overlapping time slot cursors. During refactoring, AI suggested replacing `if/elif/else` recurrence logic with a `RECURRENCE_DELTA` dict lookup and consolidating duplicate status filter methods. For testing, AI identified critical edge cases like month rollover and exact-same-start-time conflicts, then helped draft the pytest functions.

- What kinds of prompts or questions were most helpful?

The most effective prompts were specific and tied to the actual code:
- *"What are the missing relationships or logic bottlenecks in this implementation?"* — surfaced structural gaps not obvious from reading the code alone.
- *"How could this algorithm be simplified for better readability or performance?"* — produced concrete refactor suggestions with clear tradeoffs.
- *"What are the most important edge cases to test for a scheduler with sorting and recurring tasks?"* — generated a prioritized test plan rather than generic advice.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

AI suggested replacing `0 if t.is_required else 1` in the sort key with `not t.is_required`. While technically equivalent, using `not` inside a tuple sort key requires mentally flipping a boolean to understand the ordering — the original explicit form is clearer for anyone reading the code later.

- How did you evaluate or verify what the AI suggested?

The suggestion was evaluated by asking: "Would a reader immediately understand what this sorts first?" The answer for `not t.is_required` was no — it reads as "not required goes first," which is the opposite of intent. The original was kept and the decision was documented.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

The test suite covers: task completion status (`mark_complete()`), pet task count growth, chronological sort correctness including empty and single-item lists, daily and weekly recurrence with correct `due_date` advancement, month/year rollover (March 31 → April 1), auto-appending of next occurrence to `pet.tasks`, and conflict detection for overlapping tasks, non-overlapping tasks, and exact same start times.

- Why were these tests important?

These tests target the behaviors most likely to silently fail — a recurrence off by one day, a sort that looks correct but isn't, or a conflict that goes undetected because of a `<` vs `<=` boundary. Catching these in tests prevents them from reaching the UI where they'd be invisible to the owner but wrong in output.

**b. Confidence**

- How confident are you that your scheduler works correctly?

⭐⭐⭐⭐ (4/5) — The scheduling logic, recurrence, sorting, and conflict detection are all well-covered by 12 passing tests including edge cases. Confidence is high for the backend.

- What edge cases would you test next if you had more time?

Completing the same task twice in one session, an owner with 0 available minutes, a pet with no tasks, and weekly tasks where `repeat_on` is not set — to verify graceful handling rather than silent failures.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The conflict detection and recurrence logic. Both required reasoning carefully about time arithmetic and state — `detect_conflicts()` correctly groups tasks by slot to avoid false positives across morning/evening boundaries, and `next_occurrence()` handles month rollover cleanly because `timedelta` manages it automatically. Getting both working correctly and covered by tests felt like the strongest part of the build.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

The Streamlit UI has no automated tests — all session state behavior is verified manually. I'd add integration tests using `streamlit.testing` to cover form submissions, the Save Owner/Pet flow, and the conflict warning display. I'd also redesign the task table to support inline editing rather than requiring a full clear-and-re-add cycle.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

AI is most useful when you already understand the problem well enough to evaluate its suggestions. The moments where I got the most value were not when I asked AI to write code from scratch, but when I used it to pressure-test a design I'd already drafted — asking "what's missing?" or "what could go wrong?" gave better results than "write this for me."
