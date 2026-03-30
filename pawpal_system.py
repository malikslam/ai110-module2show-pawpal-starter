from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime, timedelta, date

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
VALID_PRIORITIES = set(PRIORITY_ORDER)
SLOT_ORDER = {"morning": 0, None: 1, "evening": 2}
RECURRENCE_DELTA = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}

SLOT_STARTS = {
    "morning": datetime.strptime("8:00 AM", "%I:%M %p"),
    "evening": datetime.strptime("6:00 PM", "%I:%M %p"),
}
DEFAULT_START = datetime.strptime("12:00 PM", "%I:%M %p")


@dataclass
class Owner:
    name: str
    available_minutes_per_day: int
    preferences: str = ""


@dataclass
class Pet:
    name: str
    species: str
    age: int
    health_notes: str = ""
    owner: Optional[Owner] = None
    tasks: List["Task"] = field(default_factory=list)


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str           # "low" | "medium" | "high"
    category: str           # "walk" | "feeding" | "meds" | "grooming" | "enrichment"
    is_required: bool = False
    time_of_day_constraint: Optional[str] = None    # "morning" | "evening" | None
    frequency: str = "daily"                         # "daily" | "weekly"
    repeat_on: Optional[str] = None                  # e.g. "Monday" — for weekly tasks
    completed: bool = False
    due_date: date = field(default_factory=date.today)

    def __post_init__(self):
        """Validate that priority is one of the accepted values."""
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(f"Invalid priority '{self.priority}'. Must be one of {VALID_PRIORITIES}.")

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> "Task":
        """Return a new incomplete Task instance due on the next recurrence date.

        Uses RECURRENCE_DELTA to advance due_date by 1 day (daily) or 7 days (weekly).
        All other fields are copied from the original task; completed resets to False.
        """
        next_due = self.due_date + RECURRENCE_DELTA.get(self.frequency, timedelta(days=1))
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            is_required=self.is_required,
            time_of_day_constraint=self.time_of_day_constraint,
            frequency=self.frequency,
            repeat_on=self.repeat_on,
            completed=False,
            due_date=next_due,
        )


@dataclass
class ScheduledTask:
    task: Task
    start_time: str
    reason: str


@dataclass
class DailyPlan:
    scheduled: List[ScheduledTask] = field(default_factory=list)
    skipped: List[Task] = field(default_factory=list)

    def total_time(self) -> int:
        """Return the total scheduled time in minutes."""
        return sum(s.task.duration_minutes for s in self.scheduled)

    def explain(self) -> str:
        """Return a formatted string summarizing the full daily plan."""
        lines = [f"Daily Plan — Total time: {self.total_time()} min\n"]
        for s in self.scheduled:
            status = "✓" if s.task.completed else " "
            lines.append(
                f"  [{status}] {s.start_time}  [{s.task.priority.upper()}] {s.task.title} "
                f"({s.task.duration_minutes} min) — {s.reason}"
            )
        if self.skipped:
            lines.append("\nSkipped:")
            for t in self.skipped:
                lines.append(f"  - {t.title} ({t.duration_minutes} min)")
        return "\n".join(lines)

    def pending(self) -> List[ScheduledTask]:
        """Return scheduled tasks that have not been completed."""
        return [s for s in self.scheduled if not s.task.completed]

    def completed_tasks(self) -> List[ScheduledTask]:
        """Return scheduled tasks that have been completed."""
        return [s for s in self.scheduled if s.task.completed]



class Scheduler:
    def __init__(self, pet: Pet, plan_weekday: Optional[str] = None):
        """Initialize the scheduler with a pet and an optional weekday for filtering weekly tasks."""
        if pet.owner is None:
            raise ValueError("Pet must have an Owner to determine available minutes.")
        self.pet = pet
        self.tasks = pet.tasks
        self.available_minutes = pet.owner.available_minutes_per_day
        self.plan_weekday = plan_weekday  # e.g. "Monday" — used to filter weekly tasks

    def mark_task_complete(self, task: Task) -> Task:
        """Mark a task complete and append its next occurrence to the pet's task list."""
        task.mark_complete()
        next_task = task.next_occurrence()
        self.pet.tasks.append(next_task)
        return next_task

    def sort_by_time(self, scheduled: List[ScheduledTask]) -> List[ScheduledTask]:
        """Return a chronologically sorted copy of the scheduled task list.

        Parses each start_time string (e.g. '08:30 AM') into a datetime for accurate
        comparison. Does not mutate the original list.
        """
        return sorted(scheduled, key=lambda s: datetime.strptime(s.start_time, "%I:%M %p"))

    def filter_by_pet(self, scheduled: List[ScheduledTask], pet_name: str) -> List[ScheduledTask]:
        """Return scheduled tasks if this scheduler's pet matches pet_name (case-insensitive).

        Returns an empty list if the name does not match, making it safe to call
        across multiple schedulers without raising an error.
        """
        if self.pet.name.lower() == pet_name.lower():
            return scheduled
        return []

    @staticmethod
    def detect_conflicts(plans: List[tuple]) -> List[str]:
        """Check scheduled tasks across one or more (pet_name, DailyPlan) tuples for time overlaps.

        Strategy: build a timeline of (start, end) intervals per pet and flag any pair
        where one task starts before the previous one ends. Returns warning strings only —
        never raises an exception.
        """
        def to_dt(s: ScheduledTask) -> datetime:
            return datetime.strptime(s.start_time, "%I:%M %p")

        warnings = []
        for pet_name, plan in plans:
            # Group by slot so morning/evening tasks don't false-positive against each other
            slot_groups: dict = {}
            for s in plan.scheduled:
                slot_groups.setdefault(s.task.time_of_day_constraint, []).append(s)

            for tasks in slot_groups.values():
                cursor = None
                for s in sorted(tasks, key=to_dt):
                    start = to_dt(s)  # parsed once, reused below
                    end = start + timedelta(minutes=s.task.duration_minutes)
                    if cursor is not None and start < cursor:
                        warnings.append(
                            f"⚠ Conflict for {pet_name}: '{s.task.title}' starts at "
                            f"{s.start_time} but previous task ends at "
                            f"{cursor.strftime('%I:%M %p')} — overlap of "
                            f"{int((cursor - start).seconds / 60)} min"
                        )
                    cursor = max(cursor, end) if cursor else end

        return warnings

    def generate_plan(self) -> DailyPlan:
        """Sort and schedule eligible tasks into a DailyPlan based on priority, time slot, and constraints."""
        plan = DailyPlan()
        remaining = self.available_minutes

        slot_cursors = {
            "morning": SLOT_STARTS["morning"],
            "evening": SLOT_STARTS["evening"],
            None: DEFAULT_START,
        }

        # Filter: daily tasks always eligible; weekly tasks only on their repeat_on day
        eligible = [
            t for t in self.tasks
            if t.frequency == "daily"
            or (t.frequency == "weekly" and t.repeat_on == self.plan_weekday)
        ]

        # Sort by: required first, then priority, then time slot order
        sorted_tasks = sorted(
            eligible,
            key=lambda t: (
                0 if t.is_required else 1,
                PRIORITY_ORDER[t.priority],
                SLOT_ORDER[t.time_of_day_constraint],
            )
        )

        for task in sorted_tasks:
            if task.duration_minutes > remaining:
                plan.skipped.append(task)
                continue

            slot = task.time_of_day_constraint
            cursor = slot_cursors[slot]
            start = cursor.strftime("%I:%M %p")

            reason = f"{'Required. ' if task.is_required else ''}Priority: {task.priority}."
            if self.pet.owner.preferences:
                reason += f" Owner preference: {self.pet.owner.preferences}."

            plan.scheduled.append(ScheduledTask(task=task, start_time=start, reason=reason))
            slot_cursors[slot] = cursor + timedelta(minutes=task.duration_minutes)
            remaining -= task.duration_minutes

        return plan
