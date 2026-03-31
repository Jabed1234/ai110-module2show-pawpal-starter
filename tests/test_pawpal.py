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


def test_sorting_correctness():
    """Verify Scheduler.sort_by_time returns tasks in chronological order."""
    from pawpal_system import Scheduler, Owner, Pet

    now = datetime.datetime.now()
    owner = Owner(name="Test", username="test")
    p = Pet(name="Toto")
    t1 = Task(description="A", task_time=now + datetime.timedelta(hours=3))
    t2 = Task(description="B", task_time=now + datetime.timedelta(hours=1))
    t3 = Task(description="C", task_time=now + datetime.timedelta(hours=2))
    p.add_task(t1)
    p.add_task(t2)
    p.add_task(t3)
    owner.add_pet(p)

    all_tasks = owner.get_all_tasks()
    sorted_tasks = Scheduler.sort_by_time(all_tasks)
    times = [t.task_time for t in sorted_tasks]
    assert times == sorted(times)


def test_recurrence_logic_creates_next_daily():
    """Confirm that marking a daily task complete returns a next occurrence one day later."""
    from pawpal_system import Scheduler, Owner, Pet

    now = datetime.datetime.now().replace(microsecond=0)
    owner = Owner(name="R", username="r")
    pet = Pet(name="P")
    task = Task(description="Daily walk", task_time=now, frequency="daily")
    pet.add_task(task)
    owner.add_pet(pet)

    new_task = Scheduler.mark_task_complete(task)
    assert task.status == "completed"
    assert new_task is not None
    assert new_task.frequency == "daily"
    assert new_task.task_time == task.task_time + datetime.timedelta(days=1)


def test_conflict_detection_flags_duplicate_times():
    """Verify that Scheduler.detect_conflicts flags tasks scheduled at the same datetime."""
    from pawpal_system import Scheduler, Owner, Pet

    now = datetime.datetime.now().replace(microsecond=0)
    owner = Owner(name="C", username="c")
    p1 = Pet(name="P1")
    p2 = Pet(name="P2")
    t1 = Task(description="T1", task_time=now)
    t2 = Task(description="T2", task_time=now)
    p1.add_task(t1)
    p2.add_task(t2)
    owner.add_pet(p1)
    owner.add_pet(p2)

    warnings = Scheduler.detect_conflicts(owner)
    assert len(warnings) >= 1
    assert any(now.isoformat() in w for w in warnings)
