"""
Notification manager for daily task reminders
"""
import threading
import schedule
import time
from datetime import datetime
from typing import List
from task_model import Task, Priority, TaskStatus

try:
    from winotify import Notification, audio
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    print("winotify non disponible. Les notifications ne seront pas envoyées.")


class NotificationManager:
    """Manages daily notifications for tasks"""

    def __init__(self, task_manager):
        self.task_manager = task_manager
        self.scheduler_thread = None
        self.running = False

    def get_important_tasks(self) -> List[Task]:
        """Get urgent, high priority and in-progress tasks"""
        tasks = self.task_manager.get_all_tasks()
        important = []

        for task in tasks:
            # Skip completed tasks
            if task.status == TaskStatus.DONE:
                continue

            # Include urgent and high priority tasks
            if task.priority in [Priority.URGENT, Priority.HIGH]:
                important.append(task)
            # Include in-progress tasks
            elif task.status == TaskStatus.IN_PROGRESS:
                important.append(task)

        return important

    def format_notification_message(self, tasks: List[Task]) -> str:
        """Format tasks into a notification message"""
        if not tasks:
            return "Aucune tâche urgente ou en cours pour aujourd'hui !"

        # Count by type
        urgent = sum(1 for t in tasks if t.priority == Priority.URGENT)
        high = sum(1 for t in tasks if t.priority == Priority.HIGH)
        in_progress = sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS)

        message_parts = []
        if urgent > 0:
            message_parts.append(f"{urgent} urgente(s)")
        if high > 0:
            message_parts.append(f"{high} haute priorité")
        if in_progress > 0:
            message_parts.append(f"{in_progress} en cours")

        message = "Tâches : " + ", ".join(message_parts)

        # Add first 3 task titles
        if tasks:
            message += "\n\n"
            for i, task in enumerate(tasks[:3]):
                message += f"• {task.title}\n"

            if len(tasks) > 3:
                message += f"... et {len(tasks) - 3} autre(s)"

        return message

    def send_notification(self):
        """Send notification with important tasks"""
        if not NOTIFICATIONS_AVAILABLE:
            print("Notifications non disponibles sur ce système")
            return

        tasks = self.get_important_tasks()
        message = self.format_notification_message(tasks)

        try:
            toast = Notification(
                app_id="Gestionnaire de Tâches",
                title="Rappel du matin",
                msg=message,
                duration="short"
            )
            toast.show()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Notification envoyée")
        except Exception as e:
            print(f"Erreur lors de l'envoi de la notification: {e}")

    def send_test_notification(self):
        """Send a test notification immediately"""
        if not NOTIFICATIONS_AVAILABLE:
            return False

        try:
            tasks = self.get_important_tasks()
            message = self.format_notification_message(tasks)

            toast = Notification(
                app_id="Gestionnaire de Tâches",
                title="Test de notification",
                msg=message,
                duration="short"
            )
            toast.show()
            return True
        except Exception as e:
            print(f"Erreur lors du test de notification: {e}")
            return False

    def schedule_daily_notification(self, time_str: str = "09:30"):
        """Schedule daily notification at specified time (format: HH:MM)"""
        schedule.clear()  # Clear any existing schedules
        schedule.every().day.at(time_str).do(self.send_notification)
        print(f"Notification quotidienne programmée pour {time_str}")

    def run_scheduler(self):
        """Run the scheduler in background"""
        self.running = True
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def start(self, notification_time: str = "09:30"):
        """Start the notification scheduler"""
        if not NOTIFICATIONS_AVAILABLE:
            print("Les notifications ne sont pas disponibles")
            return False

        # Schedule the notification
        self.schedule_daily_notification(notification_time)

        # Start scheduler in background thread
        self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()

        print(f"Scheduler de notifications démarré (notifications à {notification_time})")
        return True

    def stop(self):
        """Stop the notification scheduler"""
        self.running = False
        schedule.clear()
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=2)
        print("Scheduler de notifications arrêté")
