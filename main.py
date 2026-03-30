from pawpal_system import Owner, Pet, Task, Scheduler, ScheduledTask

# Owner
jordan = Owner(
    name="Jordan",
    available_minutes_per_day=120,
    preferences="prefers morning walks"
)

# Pet 1 — Mochi the dog
# Intentional conflict: three morning tasks that together overflow the slot
mochi = Pet(name="Mochi", species="dog", age=3, owner=jordan)
mochi.tasks = [
    Task(title="Morning walk",       duration_minutes=30, priority="high",   category="walk",      is_required=True, time_of_day_constraint="morning"),
    Task(title="Breakfast feeding",  duration_minutes=10, priority="high",   category="feeding",   is_required=True, time_of_day_constraint="morning"),
    Task(title="Post-walk grooming", duration_minutes=20, priority="medium", category="grooming",  time_of_day_constraint="morning"),  # ← will conflict
    Task(title="Flea medication",    duration_minutes=5,  priority="high",   category="meds",      is_required=True),
    Task(title="Fetch & play",       duration_minutes=20, priority="low",    category="enrichment"),
]

# Pet 2 — Luna the cat
luna = Pet(name="Luna", species="cat", age=2, owner=jordan, health_notes="sensitive stomach")
luna.tasks = [
    Task(title="Breakfast feeding",  duration_minutes=5,  priority="high",   category="feeding",   is_required=True, time_of_day_constraint="morning"),
    Task(title="Hairball medicine",  duration_minutes=5,  priority="high",   category="meds",      is_required=True),
    Task(title="Evening feeding",    duration_minutes=5,  priority="high",   category="feeding",   is_required=True, time_of_day_constraint="evening"),
    Task(title="Grooming brush",     duration_minutes=10, priority="medium", category="grooming"),
    Task(title="Laser pointer play", duration_minutes=15, priority="low",    category="enrichment"),
]

today = "Monday"

print("=" * 55)
print(f"  TODAY'S SCHEDULE — {today}")
print("=" * 55)

all_plans = []

for pet in [mochi, luna]:
    scheduler = Scheduler(pet=pet, plan_weekday=today)
    plan = scheduler.generate_plan()
    all_plans.append((pet.name, plan))

    print(f"\n{'─' * 55}")
    print(f"  {pet.name} ({pet.species})")
    print(f"{'─' * 55}")

    sorted_schedule = scheduler.sort_by_time(plan.scheduled)
    print("\n  [Sorted by start time]")
    for s in sorted_schedule:
        badge = "🔴" if s.task.priority == "high" else "🟡" if s.task.priority == "medium" else "🟢"
        print(f"    {s.start_time}  {badge} {s.task.title} ({s.task.duration_minutes} min)")

    # Mark first two tasks complete via Scheduler
    for s in sorted_schedule[:2]:
        next_task = scheduler.mark_task_complete(s.task)
        print(f"\n  ↻ '{s.task.title}' completed — next occurrence: {next_task.due_date}")

    pending = plan.pending()
    print(f"\n  [Pending — {len(pending)} remaining]")
    for s in pending:
        print(f"    ○ {s.task.title}")

    if plan.skipped:
        print(f"\n  [Skipped — didn't fit]")
        for t in plan.skipped:
            print(f"    - {t.title} ({t.duration_minutes} min)")

# --- Force a conflict: inject a task that overlaps Mochi's 08:00 AM morning walk ---
mochi_plan = all_plans[0][1]
clash_task = Task(title="Emergency vet call", duration_minutes=20, priority="high", category="meds", time_of_day_constraint="morning")
mochi_plan.scheduled.insert(1, ScheduledTask(task=clash_task, start_time="08:15 AM", reason="Manual override — overlaps morning walk"))

# --- Cross-pet conflict detection ---
print(f"\n{'─' * 55}")
print("  [Conflict Detection — all pets]")
print(f"{'─' * 55}")
conflicts = Scheduler.detect_conflicts(all_plans)
if conflicts:
    for warning in conflicts:
        print(f"  {warning}")
else:
    print("  No conflicts detected.")

print("\n" + "=" * 55)
