import datetime

from pawpal_system import Task, Pet


def test_task_mark_complete_changes_status():
    now = datetime.datetime.now()
    t = Task(description="Test task", task_time=now)
    assert t.status == "pending"
    t.mark_complete()
    assert t.status == "completed"
    assert t.completed_at is not None


def test_pet_add_task_increases_count():
    pet = Pet(name="Buddy")
    assert len(pet.get_tasks()) == 0
    t = Task(description="Play", task_time=datetime.datetime.now())
    pet.add_task(t)
    assert len(pet.get_tasks()) == 1
