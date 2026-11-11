from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task

owner = Owner("Renzo", available_minutes=60)
rocky = Pet("Rocky", "dog", age=4)
luna = Pet("Luna", "cat", age=2)
owner.add_pet(rocky)
owner.add_pet(luna)

# added out of order on purpose, to show sorting
rocky.add_task(Task("Evening walk", "18:00", 30, priority="medium", frequency="daily"))
luna.add_task(Task("Flea medication", "12:00", 5, priority="high", frequency="weekly"))
rocky.add_task(Task("Morning walk", "07:30", 30, priority="high", frequency="daily"))
luna.add_task(Task("Feeding", "07:45", 10, priority="high", frequency="daily"))
luna.add_task(Task("Brushing", "20:00", 15, priority="low"))

scheduler = Scheduler(owner)
today = date.today()

print(f"Today's Schedule ({today.isoformat()}) for {owner.name}")
print("-" * 52)
print(scheduler.format_schedule(scheduler.todays_schedule()))

print(f"\nPlan for {owner.available_minutes} min available")
print("-" * 52)
planned, skipped = scheduler.build_plan()
print(scheduler.format_schedule(planned))
for task, reason in skipped:
    print(f"Skipped: {task.pet_name} {task.description} ({reason})")

print("\nConflicts")
print("-" * 52)
conflicts = scheduler.detect_conflicts(scheduler.todays_schedule())
for warning in conflicts:
    print(f"WARNING: {warning}")
if not conflicts:
    print("None")

print("\nLuna's tasks only")
print("-" * 52)
print(scheduler.format_schedule(scheduler.filter_tasks(scheduler.todays_schedule(), pet_name="Luna")))

feeding = luna.tasks[1]
upcoming = scheduler.complete_task(feeding)
print(f"\nCompleted '{feeding.description}'. Next one added for {upcoming.due_date.isoformat()}.")
