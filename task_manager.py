"""
Task Manager for handling task storage and retrieval
"""
import json
import os
from typing import List, Optional
from task_model import Task, TaskStatus, Priority


class TaskManager:
    """Manages tasks and handles persistence"""

    def __init__(self, data_file: str = "tasks.json"):
        self.data_file = data_file
        self.tasks: List[Task] = []
        self.next_id = 1
        self.categories = set(["Général", "Travail", "Personnel", "Urgent"])
        self.load_tasks()

    def load_tasks(self):
        """Load tasks from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(task_data) for task_data in data.get("tasks", [])]
                    self.categories = set(data.get("categories", ["Général", "Travail", "Personnel", "Urgent"]))
                    # Calculate next ID
                    if self.tasks:
                        self.next_id = max(task.id for task in self.tasks if task.id) + 1
                    else:
                        self.next_id = 1
            except Exception as e:
                print(f"Erreur lors du chargement des tâches: {e}")
                self.tasks = []
                self.next_id = 1

    def save_tasks(self):
        """Save tasks to JSON file"""
        try:
            data = {
                "tasks": [task.to_dict() for task in self.tasks],
                "categories": list(self.categories)
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des tâches: {e}")

    def add_task(self, task: Task) -> Task:
        """Add a new task"""
        task.id = self.next_id
        self.next_id += 1
        self.tasks.append(task)
        # Add category if new
        if task.category:
            self.categories.add(task.category)
        self.save_tasks()
        return task

    def update_task(self, task: Task):
        """Update an existing task"""
        for i, t in enumerate(self.tasks):
            if t.id == task.id:
                self.tasks[i] = task
                # Add category if new
                if task.category:
                    self.categories.add(task.category)
                self.save_tasks()
                return True
        return False

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID"""
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks.pop(i)
                self.save_tasks()
                return True
        return False

    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks"""
        return self.tasks

    def get_tasks_today(self) -> List[Task]:
        """Get tasks due today"""
        return [task for task in self.tasks if task.is_due_today() and task.status != TaskStatus.DONE]

    def get_tasks_upcoming(self) -> List[Task]:
        """Get upcoming tasks (future dates)"""
        return [task for task in self.tasks if task.is_upcoming()]

    def get_tasks_overdue(self) -> List[Task]:
        """Get overdue tasks"""
        return [task for task in self.tasks if task.is_overdue()]

    def get_tasks_in_progress(self) -> List[Task]:
        """Get tasks in progress"""
        return [task for task in self.tasks if task.status == TaskStatus.IN_PROGRESS]

    def get_tasks_by_category(self, category: str) -> List[Task]:
        """Get tasks by category"""
        return [task for task in self.tasks if task.category == category]

    def get_tasks_by_priority(self, priority: Priority) -> List[Task]:
        """Get tasks by priority"""
        return [task for task in self.tasks if task.priority == priority]

    def get_categories(self) -> List[str]:
        """Get all categories"""
        return sorted(list(self.categories))

    def add_category(self, category: str):
        """Add a new category"""
        self.categories.add(category)
        self.save_tasks()
