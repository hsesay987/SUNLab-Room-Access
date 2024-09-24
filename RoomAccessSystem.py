import tkinter as tk
from tkinter import ttk
from SunLabAdministration import RoomAccessSystem
from datetime import datetime
from firebase_admin import db

class AdminGUI:
    def __init__(self, head):
        self.root = head
        self.root.title("SunLAB Room Access Admin Panel")

        self.system = RoomAccessSystem()

        # For grid resizing
        self.root.grid_rowconfigure(5, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Creates labels and entry fields for ID and date range filters
        self.id_label = tk.Label(head, text="ID Filter:")
        self.id_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.id_input = tk.Entry(head)
        self.id_input.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        self.start_date_label = tk.Label(head, text="Start Date Filter (YYYY-MM-DD):")
        self.start_date_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.start_date_input = tk.Entry(head)
        self.start_date_input.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        self.end_date_label = tk.Label(head, text="End Date Filter (YYYY-MM-DD):")
        self.end_date_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.end_date_input = tk.Entry(head)
        self.end_date_input.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Dropdown menu to filter personnel
        self.role_label = tk.Label(head, text="Personnel Filter:")
        self.role_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        self.role_options = ["Any", "student", "faculty", "staff", "janitor"]
        self.role_var = tk.StringVar(value=self.role_options[0])
        self.role_dropdown = ttk.Combobox(head, textvariable=self.role_var, values=self.role_options)
        self.role_dropdown.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        # Search button to apply filters
        self.search_button = tk.Button(head, text="Search Logs", command=self.search_logs)
        self.search_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        # Displays records
        self.results_tree = ttk.Treeview(head, columns=("User ID", "Timestamp", "Personnel"), show="headings")
        self.results_tree.heading("User ID", text="User ID")
        self.results_tree.heading("Timestamp", text="Timestamp")
        self.results_tree.heading("Personnel", text="Personnel")
        self.results_tree.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Configure Treeview scrollbars
        self.tree_scroll_y = ttk.Scrollbar(head, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscroll=self.tree_scroll_y.set)
        self.tree_scroll_y.grid(row=5, column=2, sticky="ns")

        # Label to show number of logs
        self.total_logs_label = tk.Label(head, text="Total Logs: 0")
        self.total_logs_label.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

        # Makes the total logs label adjust width when resizing
        self.root.grid_rowconfigure(6, weight=0)
        self.root.grid_columnconfigure(0, weight=1)

    def search_logs(self):
        user_id = self.id_input.get()
        start_date_str = self.start_date_input.get()
        end_date_str = self.end_date_input.get()
        role_filter = self.role_var.get().lower()

        # Converts inputs to datetime objects
        start_date = None
        end_date = None
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            except ValueError:
                print("Invalid start date format. Please use YYYY-MM-DD.")

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            except ValueError:
                print("Invalid end date format. Please use YYYY-MM-DD.")

        # Fetches logs from Database
        logs_ref = db.reference('access_logs')
        logs_snapshot = logs_ref.get()

        # Clears rows before inserting new records
        for row in self.results_tree.get_children():
            self.results_tree.delete(row)

        # Initializes log counter
        log_count = 0

        # Filters logs by personnel and date if necessary
        if logs_snapshot:
            for log_id, log_records in logs_snapshot.items():
                timestamp = datetime.fromisoformat(log_records['timestamp'])
                if start_date and timestamp < start_date:
                    continue
                if end_date and timestamp > end_date:
                    continue

                # Fetches the user's record from their ID
                user_ref = db.reference(f'users/{log_records["user_id"]}')
                user_data = user_ref.get()

                if user_data:
                    user_role = user_data.get('role', 'N/A').lower()
                else:
                    user_role = 'N/A'

                if role_filter != "any" and user_role != role_filter:
                    continue

                if user_id and log_records['user_id'] != user_id:
                    continue

                # Inserts log record into the GUI
                self.results_tree.insert('', 'end', values=(
                    log_records['user_id'], log_records['timestamp'], user_role)
                )

                # Increment log count
                log_count += 1

        # Update the total logs label
        self.total_logs_label.config(text=f"Total Logs: {log_count}")

if __name__ == '__main__':
    root = tk.Tk()
    gui = AdminGUI(root)
    root.mainloop()
