import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import psycopg2
import mysql.connector

class DBMigrationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Database View to Table Migration")
        self.root.geometry("800x600")

        # Initialize variables
        self.source_sgbd = tk.StringVar()
        self.target_sgbd = tk.StringVar()
        self.source_details = {}
        self.target_details = {}
        self.view_name = tk.StringVar()
        self.source_config = {}
        self.target_config = {}

        # Flags for connectivity
        self.source_connected = False
        self.target_connected = False

        # Layout
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.root, text="Source Database", font=("Arial", 14)).pack(pady=10)
        source_frame = ttk.Frame(self.root)
        source_frame.pack(fill=tk.X, padx=20)

        ttk.Label(source_frame, text="SGBD:").grid(row=0, column=0, sticky=tk.W)
        sgbd_options = ["SQLite", "PostgreSQL", "MySQL"]
        ttk.OptionMenu(source_frame, self.source_sgbd, sgbd_options[0], *sgbd_options, command=self.show_source_fields).grid(row=0, column=1, sticky=tk.W)

        self.source_fields_frame = ttk.Frame(self.root)
        self.source_fields_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Label(self.source_fields_frame, text="View Name:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(self.source_fields_frame, textvariable=self.view_name, width=30).grid(row=0, column=1, sticky=tk.W)

        self.connect_source_button = ttk.Button(self.source_fields_frame, text="Test Source Connectivity", command=self.connect_source)
        self.connect_source_button.grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Label(self.root, text="Target Database", font=("Arial", 14)).pack(pady=10)
        target_frame = ttk.Frame(self.root)
        target_frame.pack(fill=tk.X, padx=20)

        ttk.Label(target_frame, text="SGBD:").grid(row=0, column=0, sticky=tk.W)
        ttk.OptionMenu(target_frame, self.target_sgbd, sgbd_options[0], *sgbd_options, command=self.show_target_fields).grid(row=0, column=1, sticky=tk.W)

        self.target_fields_frame = ttk.Frame(self.root)
        self.target_fields_frame.pack(fill=tk.X, padx=20, pady=10)

        self.connect_target_button = ttk.Button(self.target_fields_frame, text="Test Target Connectivity", command=self.connect_target)
        self.connect_target_button.grid(row=0, column=0, columnspan=2, pady=10)

        self.migrate_button = ttk.Button(self.root, text="Migrate View to Tables", command=self.migrate_view_to_tables, state=tk.DISABLED)
        self.migrate_button.pack(pady=20)

        self.log_text = tk.Text(self.root, wrap=tk.WORD, height=10)
        self.log_text.pack(fill=tk.BOTH, padx=20, pady=10)

    def show_source_fields(self, sgbd):
        for widget in self.source_fields_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.source_fields_frame, text="View Name:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(self.source_fields_frame, textvariable=self.view_name, width=30).grid(row=0, column=1, sticky=tk.W)

        if sgbd != "SQLite":
            fields = ["Host", "Port", "Database Name", "Username", "Password"]
            for i, field in enumerate(fields):
                ttk.Label(self.source_fields_frame, text=f"{field}:").grid(row=i+1, column=0, sticky=tk.W)
                self.source_config[field.lower().replace(" ", "_")] = tk.StringVar()
                ttk.Entry(self.source_fields_frame, textvariable=self.source_config[field.lower().replace(" ", "_")], width=30, show="*" if field == "Password" else None).grid(row=i+1, column=1, sticky=tk.W)

        self.connect_source_button = ttk.Button(self.source_fields_frame, text="Test Source Connectivity", command=self.connect_source)
        self.connect_source_button.grid(row=len(fields)+1 if sgbd != "SQLite" else 1, column=0, columnspan=2, pady=10)

    def show_target_fields(self, sgbd):
        for widget in self.target_fields_frame.winfo_children():
            widget.destroy()

        if sgbd != "SQLite":
            fields = ["Host", "Port", "Database Name", "Username", "Password"]
            for i, field in enumerate(fields):
                ttk.Label(self.target_fields_frame, text=f"{field}:").grid(row=i, column=0, sticky=tk.W)
                self.target_config[field.lower().replace(" ", "_")] = tk.StringVar()
                ttk.Entry(self.target_fields_frame, textvariable=self.target_config[field.lower().replace(" ", "_")], width=30, show="*" if field == "Password" else None).grid(row=i, column=1, sticky=tk.W)

        self.connect_target_button = ttk.Button(self.target_fields_frame, text="Test Target Connectivity", command=self.connect_target)
        self.connect_target_button.grid(row=len(fields), column=0, columnspan=2, pady=10)

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def connect_source(self):
        sgbd = self.source_sgbd.get()
        view_name = self.view_name.get()
        if not view_name:
            messagebox.showerror("Error", "Please enter the view name.")
            return

        try:
            if sgbd == "SQLite":
                file_path = filedialog.askopenfilename(filetypes=[("SQLite Files", "*.db")])
                if file_path:
                    self.source_details = {
                        "connection": sqlite3.connect(file_path),
                        "view_name": view_name
                    }
                    self.source_connected = True
                    self.log(f"Connected to SQLite database at {file_path}.")
            elif sgbd == "PostgreSQL":
                conn = psycopg2.connect(
                    dbname=self.source_config["database_name"].get(),
                    user=self.source_config["username"].get(),
                    password=self.source_config["password"].get(),
                    host=self.source_config["host"].get(),
                    port=self.source_config["port"].get()
                )
                self.source_details = {"connection": conn, "view_name": view_name}
                self.source_connected = True
                self.log("Connected to PostgreSQL database.")
            elif sgbd == "MySQL":
                conn = mysql.connector.connect(
                    database=self.source_config["database_name"].get(),
                    user=self.source_config["username"].get(),
                    password=self.source_config["password"].get(),
                    host=self.source_config["host"].get(),
                    port=self.source_config["port"].get()
                )
                self.source_details = {"connection": conn, "view_name": view_name}
                self.source_connected = True
                self.log("Connected to MySQL database.")
        except Exception as e:
            self.source_connected = False
            self.log(f"Error connecting to source database: {e}")

        self.update_migrate_button_state()

    def connect_target(self):
        sgbd = self.target_sgbd.get()
        try:
            if sgbd == "SQLite":
                file_path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("SQLite Files", "*.db")])
                if file_path:
                    conn = sqlite3.connect(file_path)
                    self.target_details = {"connection": conn}
                    self.target_connected = True
                    self.log(f"Connected to SQLite database at {file_path}.")
            elif sgbd == "PostgreSQL":
                conn = psycopg2.connect(
                    dbname=self.target_config["database_name"].get(),
                    user=self.target_config["username"].get(),
                    password=self.target_config["password"].get(),
                    host=self.target_config["host"].get(),
                    port=self.target_config["port"].get()
                )
                self.target_details = {"connection": conn}
                self.target_connected = True
                self.log("Connected to PostgreSQL database.")
            elif sgbd == "MySQL":
                conn = mysql.connector.connect(
                    database=self.target_config["database_name"].get(),
                    user=self.target_config["username"].get(),
                    password=self.target_config["password"].get(),
                    host=self.target_config["host"].get(),
                    port=self.target_config["port"].get()
                )
                self.target_details = {"connection": conn}
                self.target_connected = True
                self.log("Connected to MySQL database.")
        except Exception as e:
            self.target_connected = False
            self.log(f"Error connecting to target database: {e}")

        self.update_migrate_button_state()

    def update_migrate_button_state(self):
        if self.source_connected and self.target_connected:
            self.migrate_button.config(state=tk.NORMAL)
        else:
            self.migrate_button.config(state=tk.DISABLED)

    def migrate_view_to_tables(self):
        try:
            source_conn = self.source_details.get("connection")
            view_name = self.source_details.get("view_name")
            target_conn = self.target_details.get("connection")

            if not source_conn or not target_conn:
                messagebox.showerror("Error", "Please connect to both source and target databases.")
                return

            # Extract view structure and data
            cursor = source_conn.cursor()
            cursor.execute(f"PRAGMA table_info({view_name})")
            columns = cursor.fetchall()
            column_definitions = ", ".join([f"{col[1]} {col[2]}" for col in columns])

            # Create table in target database
            target_cursor = target_conn.cursor()
            target_table_name = view_name + "_migrated"
            target_cursor.execute(f"CREATE TABLE {target_table_name} ({column_definitions})")

            # Copy data from view to table
            cursor.execute(f"SELECT * FROM {view_name}")
            rows = cursor.fetchall()
            placeholders = ", ".join(["?" for _ in columns])
            target_cursor.executemany(f"INSERT INTO {target_table_name} VALUES ({placeholders})", rows)

            target_conn.commit()
            self.log(f"Migration complete. Data copied to table: {target_table_name}")

        except Exception as e:
            self.log(f"Error during migration: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DBMigrationApp(root)
    root.mainloop()
