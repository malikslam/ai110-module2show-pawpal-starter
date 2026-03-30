import pytest
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler, ScheduledTask, DailyPlan


# --- Fixtures ---

@pytest.fixture
def owner():
    return Owner(name="Jordan", available_minutes_per_day=120)

@pytest.fixture
def pet(owner):
    return Pet(name="Mochi", species="dog", age=3, owner=owner)

@pytest.fixture
def scheduler(pet):
    return Scheduler(pet=pet, plan_weekday="Monday")


# --- Original tests ---

def test_mark_complete_changes_status():
    """mark_complete() should flip completed from False to True."""
    task = Task(title="Morning walk", duration_minutes=30, priority="high", category="walk")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    """Appending tasks to pet.tasks should increase the count correctly."""
    owner = Owner(name="Jordan", available_minutes_per_day=120)
    pet = Pet(name="Mochi", species="dog", age=6, owner=owner)
    assert len(pet.tasks) == 0

    pet.tasks.append(Task(title="Feeding", duration_minutes=10, priority="high", category="feeding"))
    assert len(pet.tasks) == 1

    pet.tasks.append(Task(title="Evening walk", duration_minutes=20, priority="medium", category="walk"))
    assert len(pet.tasks) == 2


# --- Sorting correctness ---

def test_sort_by_time_returns_chronological_order(scheduler):
    """Tasks added out of order should be sorted by start time ascending."""
    scheduled = [
        ScheduledTask(task=Task(title="Evening walk", duration_minutes=20, priority="medium", category="walk"), start_time="06:00 PM", reason=""),
        ScheduledTask(task=Task(title="Midday meds",  duration_minutes=5,  priority="high",   category="meds"),  start_time="12:00 PM", reason=""),
        ScheduledTask(task=Task(title="Morning walk", duration_minutes=30, priority="high",   category="walk"),  start_time="08:00 AM", reason=""),
    ]
    sorted_tasks = scheduler.sort_by_time(scheduled)
    times = [s.start_time for s in sorted_tasks]
    assert times == ["08:00 AM", "12:00 PM", "06:00 PM"]


def test_sort_by_time_single_task(scheduler):
    """A single-task list should be returned unchanged."""
    scheduled = [
        ScheduledTask(task=Task(title="Feeding", duration_minutes=10, priority="high", category="feeding"), start_time="08:00 AM", reason="")
    ]
    assert scheduler.sort_by_time(scheduled) == scheduled


def test_sort_by_time_empty_list(scheduler):
    """An empty list should return an empty list without error."""
    assert scheduler.sort_by_time([]) == []


# --- Recurrence logic ---

def test_daily_task_next_occurrence_is_tomorrow():
    """Completing a daily task should produce a new task due tomorrow."""
    today = date.today()
    task = Task(title="Feeding", duration_minutes=10, priority="high", category="feeding", frequency="daily", due_date=today)
    task.mark_complete()
    next_task = task.next_occurrence()
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False


def test_weekly_task_next_occurrence_is_next_week():
    """Completing a weekly task should produce a new task due 7 days later."""
    today = date.today()
    task = Task(title="Grooming", duration_minutes=20, priority="medium", category="grooming", frequency="weekly", repeat_on="Monday", due_date=today)
    task.mark_complete()
    next_task = task.next_occurrence()
    assert next_task.due_date == today + timedelta(weeks=1)
    assert next_task.completed is False


def test_mark_task_complete_appends_next_occurrence(pet, scheduler):
    """Scheduler.mark_task_complete() should add the next occurrence to pet.tasks."""
    task = Task(title="Feeding", duration_minutes=10, priority="high", category="feeding")
    pet.tasks.append(task)
    initial_count = len(pet.tasks)
    scheduler.mark_task_complete(task)
    assert len(pet.tasks) == initial_count + 1
    assert pet.tasks[-1].completed is False
    assert pet.tasks[-1].due_date == date.today() + timedelta(days=1)


def test_next_occurrence_month_rollover():
    """next_occurrence() on the last day of a month should roll over correctly."""
    last_day = date(2026, 3, 31)
    task = Task(title="Walk", duration_minutes=20, priority="high", category="walk", due_date=last_day)
    next_task = task.next_occurrence()
    assert next_task.due_date == date(2026, 4, 1)


# --- Conflict detection ---

def test_detect_conflicts_flags_overlapping_tasks():
    """Two tasks in the same slot where the second starts before the first ends should raise a warning."""
    plan = DailyPlan()
    task_a = Task(title="Morning walk",  duration_minutes=30, priority="high", category="walk",    time_of_day_constraint="morning")
    task_b = Task(title="Vet call",      duration_minutes=20, priority="high", category="meds",    time_of_day_constraint="morning")
    plan.scheduled = [
        ScheduledTask(task=task_a, start_time="08:00 AM", reason=""),
        ScheduledTask(task=task_b, start_time="08:15 AM", reason=""),  # overlaps by 15 min
    ]
    warnings = Scheduler.detect_conflicts([("Mochi", plan)])
    assert len(warnings) == 1
    assert "Mochi" in warnings[0]
    assert "Vet call" in warnings[0]


def test_detect_conflicts_no_overlap(owner):
    """Tasks in different slots should not trigger a conflict."""
    pet = Pet(name="Mochi", species="dog", age=3, owner=owner)
    plan = DailyPlan()
    task_a = Task(title="Morning walk",  duration_minutes=30, priority="high", category="walk",    time_of_day_constraint="morning")
    task_b = Task(title="Evening walk",  duration_minutes=20, priority="medium", category="walk",  time_of_day_constraint="evening")
    plan.scheduled = [
        ScheduledTask(task=task_a, start_time="08:00 AM", reason=""),
        ScheduledTask(task=task_b, start_time="06:00 PM", reason=""),
    ]
    warnings = Scheduler.detect_conflicts([("Mochi", plan)])
    assert warnings == []


def test_detect_conflicts_exact_same_start_time(owner):
    """Two tasks starting at the exact same time should be flagged as a conflict."""
    plan = DailyPlan()
    task_a = Task(title="Feeding",   duration_minutes=10, priority="high", category="feeding")
    task_b = Task(title="Grooming",  duration_minutes=15, priority="medium", category="grooming")
    plan.scheduled = [
        ScheduledTask(task=task_a, start_time="12:00 PM", reason=""),
        ScheduledTask(task=task_b, start_time="12:00 PM", reason=""),  # exact same time
    ]
    warnings = Scheduler.detect_conflicts([("Mochi", plan)])
    assert len(warnings) >= 1
