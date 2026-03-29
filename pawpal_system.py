from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime, timedelta

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
VALID_PRIORITIES = set(PRIORITY_ORDER)

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


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str           # "low" | "medium" | "high"
    category: str           # "walk" | "feeding" | "meds" | "grooming" | "enrichment"
    is_required: bool = False
    time_of_day_constraint: Optional[str] = None    # "morning" | "evening" | None
    frequency: str = "daily"                         # "daily" | "weekly"

    def __post_init__(self):
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(f"Invalid priority '{self.priority}'. Must be one of {VALID_PRIORITIES}.")


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
        return sum(s.task.duration_minutes for s in self.scheduled)

    def explain(self) -> str:
        lines = [f"Daily Plan — Total time: {self.total_time()} min\n"]
        for s in self.scheduled:
            lines.append(
                f"  {s.start_time}  [{s.task.priority.upper()}] {s.task.title} "
                f"({s.task.duration_minutes} min) — {s.reason}"
            )
        if self.skipped:
            lines.append("\nSkipped:")
            for t in self.skipped:
                lines.append(f"  - {t.title} ({t.duration_minutes} min)")
        return "\n".join(lines)


class Scheduler:
    def __init__(self, pet: Pet, tasks: List[Task], plan_weekday: Optional[str] = None):
        if pet.owner is None:
            raise ValueError("Pet must have an Owner to determine available minutes.")
        self.pet = pet
        self.tasks = tasks
        self.available_minutes = pet.owner.available_minutes_per_day
        self.plan_weekday = plan_weekday  # e.g. "Monday" — used to filter weekly tasks

    def generate_plan(self) -> DailyPlan:
        plan = DailyPlan()
        remaining = self.available_minutes

        # Track current time per slot to avoid overlaps
        slot_cursors = {
            "morning": SLOT_STARTS["morning"],
            "evening": SLOT_STARTS["evening"],
            None: DEFAULT_START,
        }

        eligible = [
            t for t in self.tasks
            if t.frequency == "daily" or (t.frequency == "weekly" and t.category == self.plan_weekday)
        ]

        sorted_tasks = sorted(
            eligible,
            key=lambda t: (0 if t.is_required else 1, PRIORITY_ORDER[t.priority])
        )

        for task in sorted_tasks:
            if task.duration_minutes > remaining:
                plan.skipped.append(task)
                continue

            slot = task.time_of_day_constraint  # "morning" | "evening" | None
            cursor = slot_cursors[slot]
            start = cursor.strftime("%I:%M %p")

            reason = f"{'Required. ' if task.is_required else ''}Priority: {task.priority}."
            if self.pet.owner.preferences:
                reason += f" Owner preference: {self.pet.owner.preferences}."

            plan.scheduled.append(ScheduledTask(task=task, start_time=start, reason=reason))
            slot_cursors[slot] = cursor + timedelta(minutes=task.duration_minutes)
            remaining -= task.duration_minutes

        return plan
