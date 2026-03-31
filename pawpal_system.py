"""Core logic layer for PawPal+.

This file contains dataclass-based implementations for Task and Pet,
an Owner (previously `User`) that manages multiple pets, and a Scheduler
that provides querying and organization across an Owner's pets.

The design is intentionally small and CLI-friendly so the logic can be
tested before wiring into a Streamlit UI.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Iterable


@dataclass
class Task:
	"""Represents a single activity for a pet.

	Attributes
	- description: short description of the activity
	- task_time: scheduled datetime for the activity
	- frequency: optional recurrence label (e.g., 'daily', 'weekly')
	- status: 'pending' | 'completed' | 'deleted'
	- completed_at: optional datetime when the task was completed
	"""

	description: str
	task_time: datetime
	frequency: Optional[str] = None
	status: str = "pending"
	completed_at: Optional[datetime] = None

	def mark_complete(self, when: Optional[datetime] = None) -> None:
		"""Mark the task as completed and record completion time."""
		self.status = "completed"
		self.completed_at = when or datetime.now()

	def edit(self, description: Optional[str] = None, task_time: Optional[datetime] = None, frequency: Optional[str] = None) -> None:
		"""Edit the task in-place. Only supplied fields are changed."""
		if description is not None:
			self.description = description
		if task_time is not None:
			self.task_time = task_time
		if frequency is not None:
			self.frequency = frequency

	def delete(self, soft: bool = True) -> None:
		"""Soft-delete the task (set status='deleted') by default."""
		if soft:
			self.status = "deleted"
		else:
			# A hard delete is represented by the caller removing references.
			self.status = "deleted"

	def is_overdue(self, now: Optional[datetime] = None) -> bool:
		"""Return True if the task is pending and its scheduled time is before now."""
		now = now or datetime.now()
		return self.status == "pending" and self.task_time < now

	def to_dict(self) -> Dict:
		"""Return a JSON-serializable dict representation of the task."""
		return {
			"description": self.description,
			"task_time": self.task_time.isoformat(),
			"frequency": self.frequency,
			"status": self.status,
			"completed_at": self.completed_at.isoformat() if self.completed_at else None,
		}


@dataclass
class Pet:
	"""Stores pet details and a list of tasks."""

	name: str
	species: Optional[str] = None
	tasks: List[Task] = field(default_factory=list)

	def add_task(self, task: Task) -> None:
		"""Append a task to this pet's task list."""
		self.tasks.append(task)

	def remove_task(self, task: Task, quiet: bool = False) -> None:
		"""Remove a task; raise ValueError unless quiet=True."""
		try:
			self.tasks.remove(task)
		except ValueError:
			if not quiet:
				raise

	def get_tasks(self, include_deleted: bool = False) -> List[Task]:
		"""Return this pet's tasks; exclude soft-deleted tasks by default."""
		if include_deleted:
			return list(self.tasks)
		return [t for t in self.tasks if t.status != "deleted"]


@dataclass
class Owner:
	"""Manages multiple pets and provides access to their tasks.

	Previously named `User` in the UML. Kept small: add/remove pets and
	convenience accessors for tasks.
	"""

	name: str
	username: str
	pets: List[Pet] = field(default_factory=list)

	def add_pet(self, pet: Pet) -> None:
		"""Add a Pet to this owner."""
		self.pets.append(pet)

	def remove_pet(self, pet: Pet, quiet: bool = False) -> None:
		"""Remove a Pet; raise ValueError unless quiet=True."""
		try:
			self.pets.remove(pet)
		except ValueError:
			if not quiet:
				raise

	def view_pets(self) -> List[Pet]:
		"""Return a shallow copy of the owner's pets list."""
		return list(self.pets)

	def get_all_tasks(self, include_deleted: bool = False) -> List[Task]:
		"""Flatten tasks from every pet owned by this owner."""
		tasks: List[Task] = []
		for pet in self.pets:
			tasks.extend(pet.get_tasks(include_deleted=include_deleted))
		return tasks

	def find_pet(self, name: str) -> Optional[Pet]:
		"""Return the Pet with `name` or None if not found."""
		for pet in self.pets:
			if pet.name == name:
				return pet
		return None


class Scheduler:
	"""The scheduler provides queries and simple scheduling logic.

	It is intentionally stateless: callers provide an Owner (or list of pets)
	and the Scheduler returns query results.
	"""

	@staticmethod
	def all_tasks(owner: Owner, include_deleted: bool = False) -> List[Task]:
		"""Return all tasks for the owner (optionally including deleted)."""
		return owner.get_all_tasks(include_deleted=include_deleted)

	@staticmethod
	def upcoming_tasks(owner: Owner, within: timedelta = timedelta(days=7)) -> List[Task]:
		"""Return pending tasks within `within` (sorted by scheduled time)."""
		now = datetime.now()
		cutoff = now + within
		return sorted(
			[t for t in owner.get_all_tasks() if t.status == "pending" and now <= t.task_time <= cutoff],
			key=lambda t: t.task_time,
		)

	@staticmethod
	def overdue_tasks(owner: Owner) -> List[Task]:
		now = datetime.now()
		return sorted([t for t in owner.get_all_tasks() if t.is_overdue(now)], key=lambda t: t.task_time)

	@staticmethod
	def next_task(owner: Owner) -> Optional[Task]:
		tasks = [t for t in owner.get_all_tasks() if t.status == "pending"]
		if not tasks:
			return None
		return min(tasks, key=lambda t: t.task_time)

	@staticmethod
	def tasks_by_day(owner: Owner, day: date) -> Dict[str, List[Task]]:
		"""Return tasks grouped by pet name scheduled on a particular day."""
		result: Dict[str, List[Task]] = {}
		for pet in owner.view_pets():
			daily = [t for t in pet.get_tasks() if t.task_time.date() == day]
			if daily:
				result[pet.name] = sorted(daily, key=lambda t: t.task_time)
		return result

	@staticmethod
	def mark_task_complete(task: Task, when: Optional[datetime] = None) -> None:
		task.mark_complete(when=when)


if __name__ == "__main__":
	# Small CLI demo to exercise the logic layer.
	from datetime import timedelta as _td

	now = datetime.now()

	owner = Owner(name="Alice Example", username="alice")
	fido = Pet(name="Fido", species="dog")
	whiskers = Pet(name="Whiskers", species="cat")

	t1 = Task(description="Morning walk", task_time=now + _td(hours=2), frequency="daily")
	t2 = Task(description="Feed breakfast", task_time=now + _td(minutes=30))
	t3 = Task(description="Grooming", task_time=now - _td(days=1))

	fido.add_task(t1)
	fido.add_task(t2)
	whiskers.add_task(t3)

	owner.add_pet(fido)
	owner.add_pet(whiskers)

	print("All tasks:")
	for t in owner.get_all_tasks():
		print(f" - {t.description} @ {t.task_time.isoformat()} (status={t.status})")

	print("\nUpcoming tasks (next 1 day):")
	for t in Scheduler.upcoming_tasks(owner, within=_td(days=1)):
		print(f" - {t.description} @ {t.task_time.isoformat()}")

	print("\nOverdue tasks:")
	for t in Scheduler.overdue_tasks(owner):
		print(f" - {t.description} @ {t.task_time.isoformat()}")


