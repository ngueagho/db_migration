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

        # Layout
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.root, text="Source Database", font=("Arial", 14)).pack(pady=10)
        source_frame = ttk.Frame(self.root)
        source_frame.pack(fill=tk.X, padx=20)

        ttk.Label(source_frame, text="SGBD:").grid(row=0, column=0, sticky=tk.W)
        sgbd_options = ["SQLite", "PostgreSQL", "MySQL"]
        ttk.OptionMenu(source_frame, self.source_sgbd, sgbd_options[0], *sgbd_options).grid(row=0, column=1, sticky=tk.W)

        ttk.Label(source_frame, text="View Name:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(source_frame, textvariable=self.view_name, width=30).grid(row=1, column=1, sticky=tk.W)

        ttk.Button(source_frame, text="Connect", command=self.connect_source).grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Label(self.root, text="Target Database", font=("Arial", 14)).pack(pady=10)
        target_frame = ttk.Frame(self.root)
        target_frame.pack(fill=tk.X, padx=20)

        ttk.Label(target_frame, text="SGBD:").grid(row=0, column=0, sticky=tk.W)
        ttk.OptionMenu(target_frame, self.target_sgbd, sgbd_options[0], *sgbd_options).grid(row=0, column=1, sticky=tk.W)

        ttk.Button(target_frame, text="Create New Database", command=self.create_target_db).grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Button(self.root, text="Migrate View to Tables", command=self.migrate_view_to_tables).pack(pady=20)

        self.log_text = tk.Text(self.root, wrap=tk.WORD, height=10)
        self.log_text.pack(fill=tk.BOTH, padx=20, pady=10)

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
                    self.log(f"Connected to SQLite database at {file_path}.")
            elif sgbd == "PostgreSQL":
                conn = psycopg2.connect(
                    dbname=input("Enter database name: "),
                    user=input("Enter username: "),
                    password=input("Enter password: "),
                    host=input("Enter host: "),
                    port=input("Enter port: ")
                )
                self.source_details = {"connection": conn, "view_name": view_name}
                self.log("Connected to PostgreSQL database.")
            elif sgbd == "MySQL":
                conn = mysql.connector.connect(
                    database=input("Enter database name: "),
                    user=input("Enter username: "),
                    password=input("Enter password: "),
                    host=input("Enter host: "),
                    port=input("Enter port: ")
                )
                self.source_details = {"connection": conn, "view_name": view_name}
                self.log("Connected to MySQL database.")
        except Exception as e:
            self.log(f"Error connecting to source database: {e}")

    def create_target_db(self):
        sgbd = self.target_sgbd.get()
        try:
            if sgbd == "SQLite":
                file_path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("SQLite Files", "*.db")])
                if file_path:
                    conn = sqlite3.connect(file_path)
                    self.target_details = {"connection": conn}
                    self.log(f"Created SQLite database at {file_path}.")
            elif sgbd == "PostgreSQL":
                # Code to create PostgreSQL database (requires admin credentials)
                pass
            elif sgbd == "MySQL":
                # Code to create MySQL database (requires admin credentials)
                pass
        except Exception as e:
            self.log(f"Error creating target database: {e}")

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
