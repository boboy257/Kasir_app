from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel,
    QFileDialog, QMessageBox
)
from src.database import backup_database, export_produk_ke_csv, import_produk_dari_csv

class KelolaDBWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kelola Database")
        self.setGeometry(100, 100, 400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.label_info = QLabel("Fitur Kelola Database")
        layout.addWidget(self.label_info)

        # Tombol backup
        self.btn_backup = QPushButton("Backup Database")
        self.btn_backup.clicked.connect(self.backup_db)
        layout.addWidget(self.btn_backup)

        # Tombol export CSV
        self.btn_export = QPushButton("Export Produk ke CSV")
        self.btn_export.clicked.connect(self.export_csv)
        layout.addWidget(self.btn_export)

        # Tombol import CSV
        self.btn_import = QPushButton("Import Produk dari CSV")
        self.btn_import.clicked.connect(self.import_csv)
        layout.addWidget(self.btn_import)

        layout.addStretch()

    def backup_db(self):
        try:
            path = backup_database()
            QMessageBox.information(self, "Backup Berhasil", f"Database berhasil dibackup ke:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal backup: {str(e)}")

    def export_csv(self):
        try:
            path = export_produk_ke_csv()
            QMessageBox.information(self, "Export Berhasil", f"Data produk berhasil diekspor ke:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal export: {str(e)}")

    def import_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Pilih File CSV", "", "CSV Files (*.csv)")
        if not path:
            return

        try:
            import_produk_dari_csv(path)
            QMessageBox.information(self, "Import Berhasil", f"Data produk berhasil diimpor dari:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal import: {str(e)}")

    # --- INI YANG TADI KURANG ---
    def set_current_user(self, username):
        self.current_user = username