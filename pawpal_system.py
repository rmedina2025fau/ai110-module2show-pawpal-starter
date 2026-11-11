"""PawPal+ logic layer: Owner, Pet, Task, Scheduler."""

from dataclasses import dataclass, field, replace
from datetime import date, timedelta

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
REPEAT_DAYS = {"daily": 1, "weekly": 7}


def to_minutes(hhmm: str) -> int:
    """Convert "HH:MM" to minutes after midnight."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


@dataclass
class Task:
    description: str
    time: str  # "HH:MM"
    duration_minutes: int
    priority: str = "medium"  # low | medium | high
    frequency: str = "once"  # once | daily | weekly
    due_date: date = field(default_factory=date.today)
    pet_name: str = ""
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self) -> "Task | None":
        """Return a fresh copy for the next due date, or None for one-time tasks."""
        days = REPEAT_DAYS.get(self.frequency)
        if days is None:
            return None
        return replace(self, due_date=self.due_date + timedelta(days=days), completed=False)

    def end_minutes(self) -> int:
        """Minute of the day when this task ends."""
        return to_minutes(self.time) + self.duration_minutes


@dataclass
class Pet:
    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet and tag it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def task_count(self) -> int:
        """Return how many tasks this pet has."""
        return len(self.tasks)


class Owner:
    def __init__(self, name: str, available_minutes: int = 120):
        self.name = name
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> Pet | None:
        """Find a pet by name (case-insensitive), or None."""
        for pet in self.pets:
            if pet.name.lower() == name.lower():
                return pet
        return None

    def all_tasks(self) -> list[Task]:
        """Return every task across all pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def tasks_for(self, day: date) -> list[Task]:
        """Return tasks due on the given day."""
        return [t for t in self.owner.all_tasks() if t.due_date == day]

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by start time (HH:MM)."""
        return sorted(tasks, key=lambda t: to_minutes(t.time))

    def filter_tasks(
        self, tasks: list[Task], pet_name: str | None = None, completed: bool | None = None
    ) -> list[Task]:
        """Keep tasks that match the pet name and/or completion status."""
        result = tasks
        if pet_name:
            result = [t for t in result if t.pet_name.lower() == pet_name.lower()]
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        return result

    def todays_schedule(self, day: date | None = None) -> list[Task]:
        """Return the day's tasks ordered by time."""
        day = day or date.today()
        return self.sort_by_time(self.tasks_for(day))

    def build_plan(self, day: date | None = None) -> tuple[list[Task], list[tuple[Task, str]]]:
        """Pick open tasks by priority until the owner's time runs out.

        Returns (planned tasks in time order, skipped tasks with a reason).
        """
        day = day or date.today()
        open_tasks = self.filter_tasks(self.tasks_for(day), completed=False)
        by_priority = sorted(
            open_tasks, key=lambda t: (PRIORITY_RANK.get(t.priority, 1), to_minutes(t.time))
        )
        planned: list[Task] = []
        skipped: list[tuple[Task, str]] = []
        minutes_left = self.owner.available_minutes
        for task in by_priority:
            if task.duration_minutes <= minutes_left:
                planned.append(task)
                minutes_left -= task.duration_minutes
            else:
                skipped.append((task, f"needs {task.duration_minutes} min, only {minutes_left} left"))
        return self.sort_by_time(planned), skipped

    def explain(self, task: Task) -> str:
        """One line on why a task is in the plan."""
        return f"{task.priority} priority, {task.duration_minutes} min at {task.time}"

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return a warning for every pair of tasks whose time windows overlap."""
        warnings = []
        ordered = self.sort_by_time(tasks)
        for i, first in enumerate(ordered):
            for second in ordered[i + 1 :]:
                if first.due_date != second.due_date:
                    continue
                if to_minutes(second.time) < first.end_minutes():
                    warnings.append(
                        f"{first.pet_name} '{first.description}' ({first.time}) overlaps "
                        f"{second.pet_name} '{second.description}' ({second.time})"
                    )
        return warnings

    def complete_task(self, task: Task) -> Task | None:
        """Mark a task done. Daily/weekly tasks get their next occurrence added to the pet."""
        task.mark_complete()
        upcoming = task.next_occurrence()
        if upcoming is not None:
            pet = self.owner.get_pet(task.pet_name)
            if pet is not None:
                pet.add_task(upcoming)
        return upcoming

    def format_schedule(self, tasks: list[Task]) -> str:
        """Render tasks as a readable terminal schedule."""
        if not tasks:
            return "No tasks scheduled."
        lines = []
        for t in tasks:
            status = "x" if t.completed else " "
            lines.append(
                f"[{status}] {t.time}  {t.pet_name:<8} {t.description:<18} "
                f"{t.duration_minutes:>3} min  ({t.priority})"
            )
        return "\n".join(lines)
