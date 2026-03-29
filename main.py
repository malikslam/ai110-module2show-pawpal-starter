from pawpal_system import Owner, Pet, Task, Scheduler

# Owner
jordan = Owner(
    name="Jordan",
    available_minutes_per_day=120,
    preferences="prefers morning walks"
)

# Pet 1 — Mochi the dog
mochi = Pet(name="Mochi", species="dog", age=3, owner=jordan)
mochi.tasks = [
    Task(title="Morning walk",       duration_minutes=30, priority="high",   category="walk",       is_required=True,  time_of_day_constraint="morning"),
    Task(title="Breakfast feeding",  duration_minutes=10, priority="high",   category="feeding",    is_required=True,  time_of_day_constraint="morning"),
    Task(title="Evening walk",       duration_minutes=20, priority="medium", category="walk",       time_of_day_constraint="evening"),
    Task(title="Flea medication",    duration_minutes=5,  priority="high",   category="meds",       is_required=True),
    Task(title="Fetch & play",       duration_minutes=20, priority="low",    category="enrichment"),
]

# Pet 2 — Luna the cat
luna = Pet(name="Luna", species="cat", age=2, owner=jordan, health_notes="sensitive stomach")
luna.tasks = [
    Task(title="Breakfast feeding",  duration_minutes=5,  priority="high",   category="feeding",    is_required=True,  time_of_day_constraint="morning"),
    Task(title="Hairball medicine",  duration_minutes=5,  priority="high",   category="meds",       is_required=True),
    Task(title="Evening feeding",    duration_minutes=5,  priority="high",   category="feeding",    is_required=True,  time_of_day_constraint="evening"),
    Task(title="Grooming brush",     duration_minutes=10, priority="medium", category="grooming"),
    Task(title="Laser pointer play", duration_minutes=15, priority="low",    category="enrichment"),
]

# Generate and print schedules
today = "Saturday"

print("=" * 50)
print(f"  TODAY'S SCHEDULE — {today}")
print("=" * 50)

for pet in [mochi, luna]:
    scheduler = Scheduler(pet=pet, plan_weekday=today)
    plan = scheduler.generate_plan()
    print(f"\n--- {pet.name} ({pet.species}) ---")
    print(plan.explain())

print("\n" + "=" * 50)
