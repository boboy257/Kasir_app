from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QEvent # [TAMBAHAN] Import QEvent
from src.database import backup_database, export_produk_ke_csv, import_produk_dari_csv

class KelolaDBWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kelola Database")
        self.setGeometry(100, 100, 500, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # --- STYLE DARK MODE ---
        central_widget.setStyleSheet("""
            QWidget { background-color: #121212; color: #e0e0e0; font-family: 'Segoe UI'; font-size: 13px; }
            QLabel { font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #2196F3; }
            QPushButton { 
                background-color: #1E1E1E; border: 1px solid #444; 
                padding: 12px; border-radius: 5px; font-weight: bold; margin-bottom: 5px;
            }
            QPushButton:hover { background-color: #333; }
            QPushButton:focus { border: 2px solid #ffffff; }
        """)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)

        self.label_info = QLabel("🗄️ Fitur Kelola Database")
        self.label_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_info)

        # Tombol backup
        self.btn_backup = QPushButton("Backup Database (Simpan Data)")
        self.btn_backup.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_backup.clicked.connect(self.backup_db)
        layout.addWidget(self.btn_backup)

        # Tombol export CSV
        self.btn_export = QPushButton("Export Produk ke CSV (Excel)")
        self.btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export.clicked.connect(self.export_csv)
        layout.addWidget(self.btn_export)

        # Tombol import CSV
        self.btn_import = QPushButton("Import Produk dari CSV")
        self.btn_import.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_import.clicked.connect(self.import_csv)
        layout.addWidget(self.btn_import)

        layout.addStretch()
        
        # [PENTING] Pasang telinga ESC
        self.installEventFilter(self)

    # [LOGIKA ESC]
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Escape:
            self.close()
            return True
        return super().eventFilter(obj, event)

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

    def set_current_user(self, username):
        self.current_user = username