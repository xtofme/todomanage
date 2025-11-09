"""
Task model for the task management application
"""
from datetime import datetime
from enum import Enum
from typing import Optional
import json


class Priority(Enum):
    """Task priority levels"""
    LOW = "Basse"
    MEDIUM = "Moyenne"
    HIGH = "Haute"
    URGENT = "Urgente"


class TaskStatus(Enum):
    """Task status"""
    TODO = "À faire"
    IN_PROGRESS = "En cours"
    DONE = "Terminée"


class Task:
    """Represents a single task"""

    def __init__(
        self,
        title: str,
        description: str = "",
        category: str = "Général",
        priority: Priority = Priority.MEDIUM,
        status: TaskStatus = TaskStatus.TODO,
        due_date: Optional[str] = None,
        created_at: Optional[str] = None,
        task_id: Optional[int] = None
    ):
        self.id = task_id
        self.title = title
        self.description = description
        self.category = category
        self.priority = priority
        self.status = status
        self.due_date = due_date  # Format: YYYY-MM-DD
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> dict:
        """Convert task to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "priority": self.priority.value,
            "status": self.status.value,
            "due_date": self.due_date,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """Create task from dictionary"""
        # Find priority by value
        priority = Priority.MEDIUM
        for p in Priority:
            if p.value == data.get("priority", "Moyenne"):
                priority = p
                break

        # Find status by value
        status = TaskStatus.TODO
        for s in TaskStatus:
            if s.value == data.get("status", "À faire"):
                status = s
                break

        return cls(
            title=data["title"],
            description=data.get("description", ""),
            category=data.get("category", "Général"),
            priority=priority,
            status=status,
            due_date=data.get("due_date"),
            created_at=data.get("created_at"),
            task_id=data.get("id")
        )

    def is_due_today(self) -> bool:
        """Check if task is due today"""
        if not self.due_date:
            return False
        today = datetime.now().strftime("%Y-%m-%d")
        return self.due_date == today

    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if not self.due_date or self.status == TaskStatus.DONE:
            return False
        today = datetime.now().strftime("%Y-%m-%d")
        return self.due_date < today

    def is_upcoming(self) -> bool:
        """Check if task is upcoming (future date)"""
        if not self.due_date or self.status == TaskStatus.DONE:
            return False
        today = datetime.now().strftime("%Y-%m-%d")
        return self.due_date > today

    def __str__(self) -> str:
        return f"{self.title} [{self.priority.value}] - {self.status.value}"
