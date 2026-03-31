"""Simple CLI to print Today's Schedule using the PawPal+ logic layer.

Creates an Owner with two pets, adds tasks, and prints today's schedule.
"""

from datetime import datetime, date, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler


def pretty_time(dt: datetime) -> str:
    return dt.strftime("%H:%M")


def main() -> None:
    now = datetime.now()

    owner = Owner(name="Sam Example", username="sam")

    # Create two pets
    rover = Pet(name="Rover", species="dog")
    mittens = Pet(name="Mittens", species="cat")

    # Add tasks with different times
    # Add tasks out of chronological order to demonstrate sorting
    t1 = Task(description="Evening brushing", task_time=(now + timedelta(days=1)).replace(hour=18, minute=0, second=0, microsecond=0))
    t2 = Task(description="Feed breakfast", task_time=now.replace(hour=7, minute=30, second=0, microsecond=0))
    t3 = Task(description="Morning walk", task_time=now.replace(hour=8, minute=0, second=0, microsecond=0), frequency="daily")

    rover.add_task(t1)
    rover.add_task(t2)
    rover.add_task(t3)

    owner.add_pet(rover)
    owner.add_pet(mittens)

    # Build today's schedule
    today = date.today()
    tasks_by_pet = Scheduler.tasks_by_day(owner, day=today)

    print(f"Today's Schedule for {owner.name} ({today.isoformat()}):\n")

    if not tasks_by_pet:
        print("No tasks scheduled for today.")
        return

    for pet_name, tasks in tasks_by_pet.items():
        print(f"{pet_name}:")
        for t in tasks:
            print(f"  - {pretty_time(t.task_time)}: {t.description} (status={t.status})")
        print()

    # Demonstrate conflict detection: create a task at the same time for another pet
    conflict_time = now.replace(hour=7, minute=30, second=0, microsecond=0)
    t_conflict = Task(description="Vet call", task_time=conflict_time)
    mittens.add_task(t_conflict)

    warnings = Scheduler.detect_conflicts(owner)
    print("\nConflict warnings:")
    for w in warnings:
        print(f" - {w}")

    # Demonstrate recurring task automation: mark the morning walk complete and auto-create next occurrence
    print("\nMarking morning walk complete and creating next occurrence...")
    # find the morning walk task
    morning = next((t for t in rover.get_tasks() if "Morning walk" in t.description), None)
    if morning:
        new_task = Scheduler.mark_task_complete(morning)
        if new_task:
            # add the generated next occurrence back to the same pet
            rover.add_task(new_task)
            print(f"Created next occurrence: {new_task.description} @ {new_task.task_time.isoformat()}")
        else:
            print("No recurrence for that task.")
    else:
        print("Morning walk not found")


if __name__ == "__main__":
    main()
