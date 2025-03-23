#autre chose 

import mysql.connector
from tkinter import Tk, Label, Button, ttk, Text, Scrollbar, VERTICAL, END

class MySQLDatabaseViewerApp:
    def __init__(self, master, db_config):
        self.master = master
        self.master.title("Visualisation de Base de Données MySQL")
        self.db_config = db_config
        self.connection = None
        self.tables = []

        # Widgets
        self.label = Label(master, text="Sélectionnez une table:")
        self.label.pack(pady=5)

        self.combobox = ttk.Combobox(master, state="readonly")
        self.combobox.pack(pady=5)
        self.combobox.bind("<<ComboboxSelected>>", self.show_table_content)

        self.text = Text(master, wrap="none", height=20, width=80)
        self.text.pack(pady=5)

        self.scrollbar = Scrollbar(master, orient=VERTICAL, command=self.text.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.text.config(yscrollcommand=self.scrollbar.set)

        self.refresh_button = Button(master, text="Rafraîchir", command=self.refresh_tables)
        self.refresh_button.pack(pady=5)

        self.connect_to_db()

    def connect_to_db(self):
        """Connect to the MySQL database and retrieve table names."""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            self.refresh_tables()
        except mysql.connector.Error as e:
            self.text.insert(END, f"Erreur de connexion : {e}\n")

    def refresh_tables(self):
        """Retrieve and display table names in the dropdown menu."""
        if self.connection:
            cursor = self.connection.cursor()
            try:
                cursor.execute("SHOW TABLES;")
                self.tables = [row[0] for row in cursor.fetchall()]
                self.combobox["values"] = self.tables
                self.text.delete("1.0", END)
                self.text.insert(END, f"Tables disponibles : {', '.join(self.tables)}\n")
            except mysql.connector.Error as e:
                self.text.insert(END, f"Erreur lors de la récupération des tables : {e}\n")

    def show_table_content(self, event):
        """Display the content of the selected table."""
        table_name = self.combobox.get()
        if self.connection and table_name:
            cursor = self.connection.cursor()
            try:
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                column_names = [description[0] for description in cursor.description]
                
                # Clear the text box
                self.text.delete("1.0", END)
                
                # Display column headers
                self.text.insert(END, "\t".join(column_names) + "\n")
                self.text.insert(END, "-" * 80 + "\n")

                # Display rows
                for row in rows:
                    self.text.insert(END, "\t".join(map(str, row)) + "\n")
            except mysql.connector.Error as e:
                self.text.insert(END, f"Erreur lors de la récupération des données : {e}\n")

if __name__ == "__main__":
    # Configuration de la base de données MySQL
    db_config = {
        "host": "localhost",
        "user": "votre_utilisateur",
        "password": "votre_mot_de_passe",
        "database": "votre_base_de_donnees"
    }

    root = Tk()
    app = MySQLDatabaseViewerApp(root, db_config)
    root.mainloop()
