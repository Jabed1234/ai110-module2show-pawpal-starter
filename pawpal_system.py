"""Skeleton classes for the PawPal+ system.

This module provides dataclass-based skeletons for Task and Pet and a
User class with method stubs. These are intentionally minimal: attributes
and empty method stubs are provided so you can implement behavior later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Task:
	"""Represents a single task for a pet.

	Attributes
	- task_type: type of task (e.g., 'feed', 'walk')
	- task_time: scheduled time for the task
	- task_status: status string (e.g., 'pending', 'completed')
	"""

	task_type: str
	task_time: datetime
	task_status: str = "pending"

	def mark_complete(self) -> None:
		"""Mark the task as completed. Implementer: set status and persist as needed."""
		raise NotImplementedError

	def edit_task(
		self,
		new_type: Optional[str] = None,
		new_time: Optional[datetime] = None,
		new_status: Optional[str] = None,
	) -> None:
		"""Edit task attributes. Supply only the fields that should change."""
		raise NotImplementedError

	def delete_task(self) -> None:
		"""Remove or mark the task deleted. Implementation depends on storage."""
		raise NotImplementedError


@dataclass
class Pet:
	"""Represents a pet and its tasks."""

	name: str
	tasks: List[Task] = field(default_factory=list)

	def add_task(self, task: Task) -> None:
		"""Add a Task to this pet's task list."""
		raise NotImplementedError

	def remove_task(self, task: Task) -> None:
		"""Remove a Task from this pet's task list."""
		raise NotImplementedError

	def get_tasks(self) -> List[Task]:
		"""Return the list of tasks for this pet."""
		raise NotImplementedError


@dataclass
class User:
	"""Represents a user and their pets."""

	name: str
	username: str
	pets: List[Pet] = field(default_factory=list)

	def add_pet(self, pet: Pet) -> None:
		"""Add a Pet to the user's list."""
		raise NotImplementedError

	def remove_pet(self, pet: Pet) -> None:
		"""Remove a Pet from the user's list."""
		raise NotImplementedError

	def view_pets(self) -> List[Pet]:
		"""Return the list of pets owned by the user."""
		raise NotImplementedError

	def view_tasks(self) -> List[Task]:
		"""Return a flattened list of all tasks across all pets."""
		raise NotImplementedError

