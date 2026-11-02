from pawpal_system import Pet, Task


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
