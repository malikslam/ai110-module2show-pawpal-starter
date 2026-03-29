import pytest
from pawpal_system import Owner, Pet, Task


def test_mark_complete_changes_status():
    task = Task(title="Morning walk", duration_minutes=30, priority="high", category="walk")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    owner = Owner(name="Jordan", available_minutes_per_day=120)
    pet = Pet(name="Mochi", species="dog", age=6, owner=owner)
    assert len(pet.tasks) == 0

    pet.tasks.append(Task(title="Feeding", duration_minutes=10, priority="high", category="feeding"))
    assert len(pet.tasks) == 1

    pet.tasks.append(Task(title="Evening walk", duration_minutes=20, priority="medium", category="walk"))
    assert len(pet.tasks) == 2
