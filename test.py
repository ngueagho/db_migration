import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import psycopg2
import mysql.connector
import cx_Oracle

class DBMigrationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Database View to Table Migration")
        self.root.geometry("800x600")

        self.source_sgbd = tk.StringVar()
        self.target_sgbd = tk.StringVar()
        self.view_name = tk.StringVar()
        
        self.source_details = {}
        self.target_details = {}

        self.source_connected = False
        self.target_connected = False

        self.create_widgets()

    def create_widgets(self):
        sgbd_options = ["SQLite", "PostgreSQL", "MySQL", "Oracle"]
        
        ttk.Label(self.root, text="Source Database", font=("Arial", 14)).pack(pady=10)
        source_frame = ttk.Frame(self.root)
        source_frame.pack(fill=tk.X, padx=20)
        ttk.Label(source_frame, text="SGBD:").grid(row=0, column=0, sticky=tk.W)
        ttk.OptionMenu(source_frame, self.source_sgbd, sgbd_options[0], *sgbd_options).grid(row=0, column=1, sticky=tk.W)
        
        self.create_connection_fields(source_frame, "source")
        
        ttk.Label(self.root, text="View Name:").pack(pady=5)
        ttk.Entry(self.root, textvariable=self.view_name, width=30).pack()
        
        ttk.Label(self.root, text="Target Database", font=("Arial", 14)).pack(pady=10)
        target_frame = ttk.Frame(self.root)
        target_frame.pack(fill=tk.X, padx=20)
        ttk.Label(target_frame, text="SGBD:").grid(row=0, column=0, sticky=tk.W)
        ttk.OptionMenu(target_frame, self.target_sgbd, sgbd_options[0], *sgbd_options).grid(row=0, column=1, sticky=tk.W)
        
        self.create_connection_fields(target_frame, "target")
        
        self.migrate_button = ttk.Button(self.root, text="Migrate View to Table", command=self.migrate_view_to_table, state=tk.DISABLED)
        self.migrate_button.pack(pady=10)
        
        self.update_button = ttk.Button(self.root, text="Update Table", command=self.update_table, state=tk.DISABLED)
        self.update_button.pack(pady=10)
        
        self.log_text = tk.Text(self.root, wrap=tk.WORD, height=10)
        self.log_text.pack(fill=tk.BOTH, padx=20, pady=10)
    
    def create_connection_fields(self, parent, db_type):
        ttk.Label(parent, text="Host:").grid(row=1, column=0, sticky=tk.W)
        host_entry = ttk.Entry(parent)
        host_entry.grid(row=1, column=1)
        
        ttk.Label(parent, text="Port:").grid(row=2, column=0, sticky=tk.W)
        port_entry = ttk.Entry(parent)
        port_entry.grid(row=2, column=1)
        
        ttk.Label(parent, text="Database Name:").grid(row=3, column=0, sticky=tk.W)
        db_entry = ttk.Entry(parent)
        db_entry.grid(row=3, column=1)
        
        ttk.Label(parent, text="User:").grid(row=4, column=0, sticky=tk.W)
        user_entry = ttk.Entry(parent)
        user_entry.grid(row=4, column=1)
        
        ttk.Label(parent, text="Password:").grid(row=5, column=0, sticky=tk.W)
        password_entry = ttk.Entry(parent, show="*")
        password_entry.grid(row=5, column=1)
        
        ttk.Button(parent, text="Connect", command=lambda: self.save_config(db_type, host_entry, port_entry, db_entry, user_entry, password_entry)).grid(row=6, columnspan=2, pady=5)
    
    def save_config(self, db_type, host_entry, port_entry, db_entry, user_entry, password_entry):
        details = {
            "host": host_entry.get(),
            "port": port_entry.get(),
            "database": db_entry.get(),
            "user": user_entry.get(),
            "password": password_entry.get()
        }
        try:
            sgbd = self.source_sgbd.get() if db_type == "source" else self.target_sgbd.get()
            if sgbd == "SQLite":
                file_path = filedialog.askopenfilename(filetypes=[["SQLite Files", "*.db"]])
                if file_path:
                    details["conn"] = sqlite3.connect(file_path)
            else:
                connection_classes = {"PostgreSQL": psycopg2.connect, "MySQL": mysql.connector.connect, "Oracle": cx_Oracle.connect}
                if sgbd == "Oracle":
                    dsn = cx_Oracle.makedsn(details["host"], details["port"], service_name=details["database"])
                    details["conn"] = cx_Oracle.connect(dsn=dsn, user=details["user"], password=details["password"])
                else:
                    details["conn"] = connection_classes[sgbd](**details)
            
            if db_type == "source":
                self.source_details = details
                self.source_connected = True
            else:
                self.target_details = details
                self.target_connected = True
            
            self.log(f"{db_type.capitalize()} connection established successfully.")
        except Exception as e:
            self.log(f"{db_type.capitalize()} connection failed: {e}")
        self.update_migrate_button_state()
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
    
    def update_migrate_button_state(self):
        if self.source_connected and self.target_connected:
            self.migrate_button.config(state=tk.NORMAL)
            self.update_button.config(state=tk.NORMAL)
    
    def migrate_view_to_table(self):
        try:
            source_conn = self.source_details["conn"]
            target_conn = self.target_details["conn"]
            view_name = self.view_name.get()
            cursor = source_conn.cursor()
            cursor.execute(f"SELECT * FROM {view_name}")
            rows = cursor.fetchall()
            col_names = [desc[0] for desc in cursor.description]
            
            create_table_query = f"CREATE TABLE IF NOT EXISTS {view_name} (" + ", ".join([f"{col} TEXT" for col in col_names]) + ")"
            target_cursor = target_conn.cursor()
            target_cursor.execute(create_table_query)
            target_conn.commit()
            
            target_cursor.executemany(f"INSERT INTO {view_name} VALUES (" + ", ".join(["%s"] * len(col_names)) + ")", rows)
            target_conn.commit()
            
            self.log("Migration completed successfully.")
        except Exception as e:
            self.log(f"Migration failed: {e}")
    
    def update_table(self):
        self.log("Updating table with new or modified records...")
        # Implémentation de la mise à jour des enregistrements

if __name__ == "__main__":
    root = tk.Tk()
    app = DBMigrationApp(root)
    root.mainloop()
