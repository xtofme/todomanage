"""
Dialog for adding/editing tasks
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional
try:
    from tkcalendar import DateEntry
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False
from task_model import Task, Priority, TaskStatus
from task_manager import TaskManager


class TaskDialog:
    """Dialog for creating or editing a task"""

    def __init__(self, parent, task_manager: TaskManager, task: Optional[Task] = None):
        self.task_manager = task_manager
        self.task = task
        self.result = None

        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Modifier la tâche" if task else "Nouvelle tâche")
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.setup_ui()

        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def setup_ui(self):
        """Setup the dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="Titre *", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.title_var = tk.StringVar(value=self.task.title if self.task else "")
        title_entry = ttk.Entry(main_frame, textvariable=self.title_var, width=50)
        title_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        title_entry.focus()

        # Description
        ttk.Label(main_frame, text="Description", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.description_text = tk.Text(main_frame, height=5, width=50)
        self.description_text.grid(row=3, column=0, columnspan=2,
                                  sticky=(tk.W, tk.E), pady=(0, 15))
        if self.task and self.task.description:
            self.description_text.insert("1.0", self.task.description)

        # Category
        ttk.Label(main_frame, text="Catégorie", font=("Arial", 10, "bold")).grid(
            row=4, column=0, sticky=tk.W, pady=(0, 5))

        category_frame = ttk.Frame(main_frame)
        category_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        self.category_var = tk.StringVar(value=self.task.category if self.task else "Général")
        self.category_combo = ttk.Combobox(category_frame, textvariable=self.category_var,
                                          values=self.task_manager.get_categories(),
                                          width=30)
        self.category_combo.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(category_frame, text="Nouvelle catégorie",
                  command=self.add_category).pack(side=tk.LEFT)

        # Priority
        ttk.Label(main_frame, text="Priorité", font=("Arial", 10, "bold")).grid(
            row=6, column=0, sticky=tk.W, pady=(0, 5))

        self.priority_var = tk.StringVar(
            value=self.task.priority.value if self.task else Priority.MEDIUM.value)
        priority_frame = ttk.Frame(main_frame)
        priority_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        for priority in Priority:
            ttk.Radiobutton(priority_frame, text=priority.value,
                          variable=self.priority_var,
                          value=priority.value).pack(side=tk.LEFT, padx=5)

        # Status
        ttk.Label(main_frame, text="Statut", font=("Arial", 10, "bold")).grid(
            row=8, column=0, sticky=tk.W, pady=(0, 5))

        self.status_var = tk.StringVar(
            value=self.task.status.value if self.task else TaskStatus.TODO.value)
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        for status in TaskStatus:
            ttk.Radiobutton(status_frame, text=status.value,
                          variable=self.status_var,
                          value=status.value).pack(side=tk.LEFT, padx=5)

        # Due Date
        ttk.Label(main_frame, text="Date d'échéance", font=("Arial", 10, "bold")).grid(
            row=10, column=0, sticky=tk.W, pady=(0, 5))

        date_frame = ttk.Frame(main_frame)
        date_frame.grid(row=11, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        self.date_enabled = tk.BooleanVar(value=bool(self.task and self.task.due_date))
        ttk.Checkbutton(date_frame, text="Définir une date d'échéance",
                       variable=self.date_enabled,
                       command=self.toggle_date).pack(side=tk.LEFT, padx=(0, 10))

        if CALENDAR_AVAILABLE:
            initial_date = None
            if self.task and self.task.due_date:
                try:
                    initial_date = datetime.strptime(self.task.due_date, "%Y-%m-%d")
                except:
                    initial_date = datetime.now()
            else:
                initial_date = datetime.now()

            self.date_entry = DateEntry(date_frame, width=12, background='darkblue',
                                       foreground='white', borderwidth=2,
                                       date_pattern='yyyy-mm-dd',
                                       year=initial_date.year,
                                       month=initial_date.month,
                                       day=initial_date.day)
            self.date_entry.pack(side=tk.LEFT)
        else:
            self.date_var = tk.StringVar(value=self.task.due_date if self.task and self.task.due_date else "")
            ttk.Label(date_frame, text="AAAA-MM-JJ:").pack(side=tk.LEFT, padx=(0, 5))
            self.date_entry = ttk.Entry(date_frame, textvariable=self.date_var, width=15)
            self.date_entry.pack(side=tk.LEFT)

        self.toggle_date()

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=12, column=0, columnspan=2, pady=(20, 0))

        ttk.Button(button_frame, text="Enregistrer",
                  command=self.save_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Annuler",
                  command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)

    def toggle_date(self):
        """Enable/disable date entry based on checkbox"""
        if self.date_enabled.get():
            self.date_entry.config(state="normal")
        else:
            self.date_entry.config(state="disabled")

    def add_category(self):
        """Add a new category"""
        category_dialog = tk.Toplevel(self.dialog)
        category_dialog.title("Nouvelle catégorie")
        category_dialog.geometry("300x100")
        category_dialog.transient(self.dialog)
        category_dialog.grab_set()

        frame = ttk.Frame(category_dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Nom de la catégorie:").pack(pady=(0, 10))
        category_var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=category_var, width=30)
        entry.pack(pady=(0, 10))
        entry.focus()

        def save_category():
            category = category_var.get().strip()
            if category:
                self.task_manager.add_category(category)
                self.category_combo['values'] = self.task_manager.get_categories()
                self.category_var.set(category)
                category_dialog.destroy()

        ttk.Button(frame, text="Ajouter", command=save_category).pack()

    def save_task(self):
        """Save the task"""
        # Validate title
        title = self.title_var.get().strip()
        if not title:
            messagebox.showerror("Erreur", "Le titre est obligatoire")
            return

        # Get description
        description = self.description_text.get("1.0", tk.END).strip()

        # Get category
        category = self.category_var.get().strip()
        if not category:
            category = "Général"

        # Get priority
        priority = Priority.MEDIUM
        for p in Priority:
            if p.value == self.priority_var.get():
                priority = p
                break

        # Get status
        status = TaskStatus.TODO
        for s in TaskStatus:
            if s.value == self.status_var.get():
                status = s
                break

        # Get due date
        due_date = None
        if self.date_enabled.get():
            if CALENDAR_AVAILABLE:
                due_date = self.date_entry.get_date().strftime("%Y-%m-%d")
            else:
                date_str = self.date_var.get().strip()
                if date_str:
                    # Validate date format
                    try:
                        datetime.strptime(date_str, "%Y-%m-%d")
                        due_date = date_str
                    except ValueError:
                        messagebox.showerror("Erreur",
                                           "Format de date invalide. Utilisez AAAA-MM-JJ")
                        return

        # Create task
        self.result = Task(
            title=title,
            description=description,
            category=category,
            priority=priority,
            status=status,
            due_date=due_date
        )

        self.dialog.destroy()
