"""
Main GUI application for Task Management
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional
from task_model import Task, Priority, TaskStatus
from task_manager import TaskManager
from task_dialog import TaskDialog
from notification_manager import NotificationManager


class TaskManagerApp:
    """Main application window"""

    def __init__(self, root):
        self.root = root
        self.root.title("Gestionnaire de Tâches")
        self.root.geometry("1000x700")

        self.task_manager = TaskManager()
        self.current_filter = "all"

        # Initialize notification manager
        self.notification_manager = NotificationManager(self.task_manager)
        self.notification_enabled = False

        self.setup_ui()
        self.refresh_task_list()

        # Start notifications if available
        if self.notification_manager.start("09:30"):
            self.notification_enabled = True
            self.status_var.set("Prêt - Notifications activées (9h30)")

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="Gestionnaire de Tâches",
                               font=("Arial", 20, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 10))

        # Filter buttons frame
        filter_frame = ttk.Frame(main_frame)
        filter_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(filter_frame, text="Toutes",
                  command=lambda: self.set_filter("all")).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Aujourd'hui",
                  command=lambda: self.set_filter("today")).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="À venir",
                  command=lambda: self.set_filter("upcoming")).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="En retard",
                  command=lambda: self.set_filter("overdue")).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="En cours",
                  command=lambda: self.set_filter("in_progress")).pack(side=tk.LEFT, padx=5)

        # Task list frame
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Treeview for tasks
        columns = ("Titre", "Catégorie", "Priorité", "Statut", "Échéance")
        self.task_tree = ttk.Treeview(list_frame, columns=columns, show="tree headings",
                                     selectmode="browse")

        # Configure columns
        self.task_tree.column("#0", width=50, minwidth=50)
        self.task_tree.column("Titre", width=250, minwidth=150)
        self.task_tree.column("Catégorie", width=120, minwidth=80)
        self.task_tree.column("Priorité", width=100, minwidth=80)
        self.task_tree.column("Statut", width=100, minwidth=80)
        self.task_tree.column("Échéance", width=100, minwidth=80)

        # Configure headings
        self.task_tree.heading("#0", text="ID")
        self.task_tree.heading("Titre", text="Titre")
        self.task_tree.heading("Catégorie", text="Catégorie")
        self.task_tree.heading("Priorité", text="Priorité")
        self.task_tree.heading("Statut", text="Statut")
        self.task_tree.heading("Échéance", text="Échéance")

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)

        self.task_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Double-click to edit
        self.task_tree.bind("<Double-1>", self.on_task_double_click)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))

        ttk.Button(button_frame, text="Nouvelle tâche",
                  command=self.add_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Modifier",
                  command=self.edit_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Supprimer",
                  command=self.delete_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Marquer terminée",
                  command=self.mark_done).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualiser",
                  command=self.refresh_task_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔔 Test notification",
                  command=self.test_notification).pack(side=tk.LEFT, padx=5)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Prêt")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var,
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

    def set_filter(self, filter_type: str):
        """Set the current filter"""
        self.current_filter = filter_type
        self.refresh_task_list()

    def refresh_task_list(self):
        """Refresh the task list based on current filter"""
        # Clear existing items
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)

        # Get filtered tasks
        if self.current_filter == "all":
            tasks = self.task_manager.get_all_tasks()
            filter_label = "Toutes les tâches"
        elif self.current_filter == "today":
            tasks = self.task_manager.get_tasks_today()
            filter_label = "Tâches d'aujourd'hui"
        elif self.current_filter == "upcoming":
            tasks = self.task_manager.get_tasks_upcoming()
            filter_label = "Tâches à venir"
        elif self.current_filter == "overdue":
            tasks = self.task_manager.get_tasks_overdue()
            filter_label = "Tâches en retard"
        elif self.current_filter == "in_progress":
            tasks = self.task_manager.get_tasks_in_progress()
            filter_label = "Tâches en cours"
        else:
            tasks = self.task_manager.get_all_tasks()
            filter_label = "Toutes les tâches"

        # Add tasks to tree
        for task in tasks:
            due_date_str = task.due_date if task.due_date else "Aucune"

            # Color code based on priority and status
            tags = []
            if task.is_overdue():
                tags.append("overdue")
            elif task.status == TaskStatus.DONE:
                tags.append("done")
            elif task.priority == Priority.URGENT:
                tags.append("urgent")
            elif task.priority == Priority.HIGH:
                tags.append("high")

            self.task_tree.insert("", tk.END, text=str(task.id),
                                 values=(task.title, task.category,
                                        task.priority.value, task.status.value,
                                        due_date_str),
                                 tags=tags)

        # Configure tags for colors
        self.task_tree.tag_configure("overdue", background="#ffcccc")
        self.task_tree.tag_configure("done", foreground="#999999")
        self.task_tree.tag_configure("urgent", background="#ff9999")
        self.task_tree.tag_configure("high", background="#ffdd99")

        self.status_var.set(f"{filter_label}: {len(tasks)} tâche(s)")

    def add_task(self):
        """Open dialog to add a new task"""
        dialog = TaskDialog(self.root, self.task_manager)
        self.root.wait_window(dialog.dialog)

        if dialog.result:
            self.task_manager.add_task(dialog.result)
            self.refresh_task_list()
            self.status_var.set(f"Tâche '{dialog.result.title}' ajoutée")

    def edit_task(self):
        """Edit the selected task"""
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("Aucune sélection",
                                  "Veuillez sélectionner une tâche à modifier")
            return

        task_id = int(self.task_tree.item(selection[0])["text"])
        task = self.task_manager.get_task(task_id)

        if task:
            dialog = TaskDialog(self.root, self.task_manager, task)
            self.root.wait_window(dialog.dialog)

            if dialog.result:
                dialog.result.id = task_id
                self.task_manager.update_task(dialog.result)
                self.refresh_task_list()
                self.status_var.set(f"Tâche '{dialog.result.title}' modifiée")

    def delete_task(self):
        """Delete the selected task"""
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("Aucune sélection",
                                  "Veuillez sélectionner une tâche à supprimer")
            return

        task_id = int(self.task_tree.item(selection[0])["text"])
        task = self.task_manager.get_task(task_id)

        if task and messagebox.askyesno("Confirmer",
                                        f"Supprimer la tâche '{task.title}' ?"):
            self.task_manager.delete_task(task_id)
            self.refresh_task_list()
            self.status_var.set(f"Tâche '{task.title}' supprimée")

    def mark_done(self):
        """Mark the selected task as done"""
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("Aucune sélection",
                                  "Veuillez sélectionner une tâche à marquer comme terminée")
            return

        task_id = int(self.task_tree.item(selection[0])["text"])
        task = self.task_manager.get_task(task_id)

        if task:
            task.status = TaskStatus.DONE
            self.task_manager.update_task(task)
            self.refresh_task_list()
            self.status_var.set(f"Tâche '{task.title}' marquée comme terminée")

    def on_task_double_click(self, event):
        """Handle double-click on task"""
        self.edit_task()

    def test_notification(self):
        """Send a test notification"""
        if self.notification_manager.send_test_notification():
            self.status_var.set("Notification de test envoyée !")
        else:
            messagebox.showinfo("Notifications",
                              "Les notifications ne sont pas disponibles.\n"
                              "Installez winotify: pip install winotify")

    def on_closing(self):
        """Handle application closing"""
        # Stop notification scheduler
        if self.notification_enabled:
            self.notification_manager.stop()
        self.root.destroy()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
