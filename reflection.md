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


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
