"""PawPal+ logic layer: Owner, Pet, Task, Scheduler."""

from dataclasses import dataclass, field
from datetime import date


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
    def __init__(self, name: str):
        self.name = name
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

    def todays_schedule(self, day: date | None = None) -> list[Task]:
        """Return the day's tasks ordered by time."""
        day = day or date.today()
        return sorted(self.tasks_for(day), key=lambda t: t.time)

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
