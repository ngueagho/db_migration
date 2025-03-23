import sys
import csv
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget,
                             QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
                             QComboBox, QLabel, QTableWidget, QTableWidgetItem,
                             QProgressBar, QHBoxLayout, QFileDialog, QMessageBox, QAbstractItemView)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

class DragDropWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.layout = QVBoxLayout()
        self.label = QLabel("Drag and drop a CSV file here")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.endswith(".csv"):
                self.parent().import_csv(file_path)
            else:
                QMessageBox.warning(self, "Invalid File", "Please drop a valid CSV file.")

class DataMigrationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Migration Tool")
        self.setGeometry(100, 100, 800, 600)

        # Main tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create tabs
        self.import_tab = self.create_import_tab()
        self.connection_tab = self.create_connection_tab()
        self.tables_tab = self.create_tables_tab()
        self.mapping_tab = self.create_mapping_tab()
        self.migration_tab = self.create_migration_tab()
        self.final_tab = self.create_final_tab()

        # Add tabs to the tab widget
        self.tabs.addTab(self.import_tab, "Import CSV")
        self.tabs.addTab(self.connection_tab, "Connection")
        self.tabs.addTab(self.tables_tab, "Tables")
        self.tabs.addTab(self.mapping_tab, "Column Mapping")
        self.tabs.addTab(self.migration_tab, "Migration")
        self.tabs.addTab(self.final_tab, "Final Validation")

        self.imported_data = []
        self.db_connected = False
        self.column_mapping = {}

        # Disable tabs until prerequisites are met
        self.tabs.setTabEnabled(2, False)
        self.tabs.setTabEnabled(3, False)
        self.tabs.setTabEnabled(4, False)
        self.tabs.setTabEnabled(5, False)

    def create_import_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.drag_drop_widget = DragDropWidget(self)
        self.import_status_label = QLabel("No file imported")
        self.file_table = QTableWidget()
        self.file_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.import_button = QPushButton("Import CSV")
        self.import_button.clicked.connect(self.import_csv)

        layout.addWidget(self.drag_drop_widget)
        layout.addWidget(self.import_button)
        layout.addWidget(self.import_status_label)
        layout.addWidget(self.file_table)
        tab.setLayout(layout)

        return tab

    def import_csv(self, file_path=None):
        if not file_path:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
            # mmm

        if file_path:
            self.imported_data = []
            try:
                with open(file_path, "r") as file:
                    reader = csv.reader(file)
                    self.imported_data = list(reader)

                if not self.imported_data:
                    raise ValueError("CSV file is empty.")

                self.import_status_label.setText(f"Imported: {file_path}")
                self.populate_table(self.file_table, self.imported_data)
                # mmm



                # Enable the "Tables" tab if the connection is also validated
                if self.db_connected:
                    self.tabs.setTabEnabled(2, True)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read the file: {str(e)}")

    def populate_table(self, table_widget, data):
        table_widget.setRowCount(len(data))
        table_widget.setColumnCount(len(data[0]))
        table_widget.setHorizontalHeaderLabels(data[0])
        for row_idx, row in enumerate(data[1:]):
            for col_idx, cell in enumerate(row):
                table_widget.setItem(row_idx, col_idx, QTableWidgetItem(cell))

    def create_connection_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Form for connection details
        form_layout = QFormLayout()
        self.db_type_combo = QComboBox()
        self.db_type_combo.addItems(["MySQL", "PostgreSQL", "SQLite"])
        self.host_input = QLineEdit()
        self.port_input = QLineEdit()
        self.user_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.database_input = QLineEdit()

        form_layout.addRow("Database Type:", self.db_type_combo)
        form_layout.addRow("Host:", self.host_input)
        form_layout.addRow("Port:", self.port_input)
        form_layout.addRow("User:", self.user_input)
        form_layout.addRow("Password:", self.password_input)
        form_layout.addRow("Database:", self.database_input)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.validate_connection)
        self.connect_status_label = QLabel("Not Connected")
        self.connect_status_label.setAlignment(Qt.AlignCenter)

        layout.addLayout(form_layout)
        layout.addWidget(self.connect_button)
        layout.addWidget(self.connect_status_label)
        tab.setLayout(layout)

        return tab

    def validate_connection(self):
        try:
            db_type = self.db_type_combo.currentText()
            host = self.host_input.text()
            port = self.port_input.text()
            user = self.user_input.text()
            password = self.password_input.text()
            database = self.database_input.text()

            if db_type == "MySQL":
                import pymysql
                connection = pymysql.connect(host=host, port=int(port), user=user, password=password, database=database)
            elif db_type == "PostgreSQL":
                import psycopg2
                connection = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=database)
            elif db_type == "SQLite":
                import sqlite3
                connection = sqlite3.connect(database)
            else:
                raise ValueError("Unsupported database type.")

            self.db_connected = True
            self.connect_status_label.setText("Connected Successfully")
            QMessageBox.information(self, "Connection", "Database connected successfully.")

            if connection:
                connection.close()

            # Enable the "Tables" tab if CSV is also imported
            if self.imported_data:
                self.tabs.setTabEnabled(2, True)
        except Exception as e:
            self.db_connected = False
            self.connect_status_label.setText("Connection Failed")
            QMessageBox.critical(self, "Connection Error", f"Failed to connect: {str(e)}")

    def create_tables_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # File table
        self.file_table_view = QTableWidget()
        self.file_table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Database table
        self.db_table_combo = QComboBox()
        self.db_table_combo.currentTextChanged.connect(self.load_db_table)
        self.db_table_view = QTableWidget()
        self.db_table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        



        layout.addWidget(QLabel("Table importée (CSV):"))
        layout.addWidget(self.file_table_view)
        layout.addWidget(QLabel("Table sélectionnée (Base de données):"))
        layout.addWidget(self.db_table_combo)
        layout.addWidget(self.db_table_view)
        tab.setLayout(layout)

        return tab

    
    
    



    # def load_db_table(self, table_name):
    #     if self.db_connected:
    #         try:
    #             # Placeholder for database query logic


    #             data = [[f"Row{i+1}Col{j+1}" for j in range(5)] for i in range(10)]
    #             self.populate_table(self.db_table_view, [["ColA", "ColB", "ColC", "ColD", "ColE"]] + data)
    #         except Exception as e:
    #             QMessageBox.critical(self, "Error", f"Failed to load table: {str(e)}")

    
    def load_db_table(self, table_name):
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



    def create_mapping_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Mapping widgets
        self.mapping_layout = QVBoxLayout()
        self.mapping_widgets = []


        for i in range(5):
            mapping_row = QHBoxLayout()
            file_col = QLabel(f"File Col {i+1}")
            db_col_combo = QComboBox()

            db_col_combo.addItems(["ColA", "ColB", "ColC", "ColD", "ColE"])
            mapping_row.addWidget(file_col)
            mapping_row.addWidget(db_col_combo)
            self.mapping_layout.addLayout(mapping_row)
            self.mapping_widgets.append((file_col, db_col_combo))

        layout.addLayout(self.mapping_layout)
        tab.setLayout(layout)

        return tab

    def create_migration_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Security input
        layout.addWidget(QLabel("Enter your credentials to confirm migration:"))
        self.migration_user_input = QLineEdit()
        self.migration_password_input = QLineEdit()
        self.migration_password_input.setEchoMode(QLineEdit.Password)

        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.migration_user_input)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.migration_password_input)

        self.migrate_button = QPushButton("Start Migration")
        self.migrate_button.clicked.connect(self.start_migration)
        self.progress_bar = QProgressBar()
        layout.addWidget(self.migrate_button)
        layout.addWidget(self.progress_bar)

        tab.setLayout(layout)

        return tab

    def start_migration(self):
        if not self.migration_user_input.text() or not self.migration_password_input.text():
            QMessageBox.warning(self, "Migration", "Please enter valid credentials for migration.")
            return

        if not self.db_connected:
            QMessageBox.warning(self, "Migration", "Please connect to the database before migrating.")
            return

        if not self.imported_data:
            QMessageBox.warning(self, "Migration", "Please import a CSV file before migrating.")
            return

        # Placeholder for migration logic
        self.progress_bar.setValue(50)
        QMessageBox.information(self, "Migration", "Migration completed successfully.")
        self.progress_bar.setValue(100)

    def create_final_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Tables for validation
        self.final_table1 = QTableWidget()
        self.final_table2 = QTableWidget()

        layout.addWidget(QLabel("Final Validation - Table 1:"))
        layout.addWidget(self.final_table1)
        layout.addWidget(QLabel("Final Validation - Table 2:"))
        layout.addWidget(self.final_table2)

        self.validate_button = QPushButton("Validate and Exit")
        self.validate_button.clicked.connect(self.validate_and_exit)
        layout.addWidget(self.validate_button)

        tab.setLayout(layout)

        return tab

    def validate_and_exit(self):
        # Placeholder for final validation logic
        QMessageBox.information(self, "Validation", "Process validated. Exiting application.")
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DataMigrationApp()
    window.show()
    sys.exit(app.exec_())
