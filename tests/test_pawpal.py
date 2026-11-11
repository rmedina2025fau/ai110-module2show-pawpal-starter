from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task

DAY = date(2026, 11, 11)


def make_owner(minutes=120):
    owner = Owner("Renzo", available_minutes=minutes)
    rocky = Pet("Rocky", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(rocky)
    owner.add_pet(luna)
    return owner, rocky, luna


def test_mark_complete_changes_status():
    task = Task("Feeding", "08:00", 10)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_count():
    pet = Pet("Rocky", "dog")
    assert pet.task_count() == 0
    pet.add_task(Task("Walk", "07:30", 30))
    assert pet.task_count() == 1
    assert pet.tasks[0].pet_name == "Rocky"


def test_sort_by_time_orders_chronologically():
    owner, rocky, _ = make_owner()
    rocky.add_task(Task("Evening walk", "18:00", 30, due_date=DAY))
    rocky.add_task(Task("Morning walk", "07:30", 30, due_date=DAY))
    rocky.add_task(Task("Lunch", "12:00", 10, due_date=DAY))
    times = [t.time for t in Scheduler(owner).todays_schedule(DAY)]
    assert times == ["07:30", "12:00", "18:00"]


def test_daily_task_creates_next_day_when_completed():
    owner, _, luna = make_owner()
    luna.add_task(Task("Feeding", "08:00", 10, frequency="daily", due_date=DAY))
    upcoming = Scheduler(owner).complete_task(luna.tasks[0])
    assert luna.tasks[0].completed is True
    assert upcoming.due_date == DAY + timedelta(days=1)
    assert upcoming.completed is False
    assert luna.task_count() == 2


def test_weekly_task_moves_seven_days():
    task = Task("Flea medication", "12:00", 5, frequency="weekly", due_date=DAY)
    assert task.next_occurrence().due_date == DAY + timedelta(days=7)


def test_one_time_task_does_not_repeat():
    owner, rocky, _ = make_owner()
    rocky.add_task(Task("Vet visit", "15:00", 60, due_date=DAY))
    assert Scheduler(owner).complete_task(rocky.tasks[0]) is None
    assert rocky.task_count() == 1


def test_detect_conflicts_flags_overlap():
    owner, rocky, luna = make_owner()
    rocky.add_task(Task("Walk", "07:30", 30, due_date=DAY))
    luna.add_task(Task("Feeding", "07:45", 10, due_date=DAY))
    warnings = Scheduler(owner).detect_conflicts(owner.all_tasks())
    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Feeding" in warnings[0]


def test_back_to_back_tasks_are_not_a_conflict():
    owner, rocky, _ = make_owner()
    rocky.add_task(Task("Walk", "07:30", 30, due_date=DAY))
    rocky.add_task(Task("Feeding", "08:00", 10, due_date=DAY))
    assert Scheduler(owner).detect_conflicts(owner.all_tasks()) == []


def test_filter_by_pet_and_status():
    owner, rocky, luna = make_owner()
    rocky.add_task(Task("Walk", "07:30", 30, due_date=DAY))
    luna.add_task(Task("Feeding", "08:00", 10, due_date=DAY))
    luna.tasks[0].mark_complete()
    scheduler = Scheduler(owner)
    tasks = owner.all_tasks()
    assert [t.description for t in scheduler.filter_tasks(tasks, pet_name="luna")] == ["Feeding"]
    assert [t.description for t in scheduler.filter_tasks(tasks, completed=False)] == ["Walk"]


def test_build_plan_skips_low_priority_when_time_runs_out():
    owner, rocky, luna = make_owner(minutes=40)
    rocky.add_task(Task("Walk", "07:30", 30, priority="high", due_date=DAY))
    luna.add_task(Task("Brushing", "09:00", 15, priority="low", due_date=DAY))
    luna.add_task(Task("Feeding", "08:00", 10, priority="high", due_date=DAY))
    planned, skipped = Scheduler(owner).build_plan(DAY)
    assert [t.description for t in planned] == ["Walk", "Feeding"]
    assert [t.description for t, _ in skipped] == ["Brushing"]


def test_pet_with_no_tasks_gives_empty_schedule():
    owner, _, _ = make_owner()
    scheduler = Scheduler(owner)
    assert scheduler.todays_schedule(DAY) == []
    assert scheduler.format_schedule([]) == "No tasks scheduled."


def test_sort_handles_times_without_leading_zero():
    owner, rocky, _ = make_owner()
    rocky.add_task(Task("Lunch", "12:00", 10, due_date=DAY))
    rocky.add_task(Task("Walk", "7:30", 30, due_date=DAY))
    assert [t.description for t in Scheduler(owner).todays_schedule(DAY)] == ["Walk", "Lunch"]
