from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task

owner = Owner("Renzo")
rocky = Pet("Rocky", "dog", age=4)
luna = Pet("Luna", "cat", age=2)
owner.add_pet(rocky)
owner.add_pet(luna)

rocky.add_task(Task("Morning walk", "07:30", 30, priority="high", frequency="daily"))
rocky.add_task(Task("Evening walk", "18:00", 30, priority="medium", frequency="daily"))
luna.add_task(Task("Feeding", "08:00", 10, priority="high", frequency="daily"))
luna.add_task(Task("Flea medication", "12:00", 5, priority="high", frequency="weekly"))

scheduler = Scheduler(owner)
print(f"Today's Schedule ({date.today().isoformat()}) for {owner.name}")
print("-" * 52)
print(scheduler.format_schedule(scheduler.todays_schedule()))
