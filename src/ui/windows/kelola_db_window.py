from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel,
    QFileDialog, QMessageBox, QFrame, QHBoxLayout, QGroupBox
)
from PyQt6.QtCore import Qt, QEvent
import shutil
import os
import sqlite3
from datetime import datetime
from src.database import DB_PATH, export_produk_ke_csv, import_produk_dari_csv, create_connection

class KelolaDBWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pusat Kontrol Database")
        self.setGeometry(100, 100, 600, 550)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # --- STYLE DARK MODE ---
        self.setStyleSheet("""
            QWidget { 
                background-color: #121212; color: #e0e0e0; font-family: 'Segoe UI'; font-size: 13px; outline: none;
            }
            QGroupBox {
                border: 1px solid #333; border-radius: 5px; margin-top: 10px; font-weight: bold; color: #2196F3;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QPushButton { 
                background-color: #1E1E1E; border: 1px solid #444; padding: 12px; border-radius: 5px; text-align: left; font-weight: bold;
            }
            QPushButton:hover { background-color: #333; }
            QPushButton:focus { border: 2px solid #ffffff; background-color: #424242; }
            QLabel { color: #bbb; }
            QLabel#InfoLabel { font-size: 11px; color: #777; font-style: italic; }
        """)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # 1. INFO
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: #181818; border-radius: 5px; border: 1px solid #333;")
        info_layout = QHBoxLayout(info_frame)
        self.lbl_path = QLabel(f"Lokasi: ...{str(DB_PATH)[-35:]}") 
        self.lbl_size = QLabel("Ukuran: - KB")
        self.lbl_size.setStyleSheet("color: #4CAF50; font-weight: bold;")
        info_layout.addWidget(self.lbl_path); info_layout.addStretch(); info_layout.addWidget(self.lbl_size)
        layout.addWidget(info_frame)

        # 2. BACKUP
        grp_backup = QGroupBox("Backup & Pemulihan")
        lay_backup = QVBoxLayout()
        self.btn_backup = QPushButton("💾  Backup Database")
        self.btn_backup.clicked.connect(self.backup_db)
        self.btn_restore = QPushButton("♻️  Restore Database")
        self.btn_restore.clicked.connect(self.restore_db)
        lay_backup.addWidget(self.btn_backup); lay_backup.addWidget(self.btn_restore)
        grp_backup.setLayout(lay_backup); layout.addWidget(grp_backup)

        # 3. IMPORT EXPORT
        grp_data = QGroupBox("Migrasi Data Produk")
        lay_data = QHBoxLayout()
        self.btn_export = QPushButton("📤 Export CSV")
        self.btn_export.clicked.connect(self.export_csv)
        self.btn_import = QPushButton("📥 Import CSV")
        self.btn_import.clicked.connect(self.import_csv)
        lay_data.addWidget(self.btn_export); lay_data.addWidget(self.btn_import)
        grp_data.setLayout(lay_data); layout.addWidget(grp_data)

        # 4. MAINTENANCE
        grp_maint = QGroupBox("Maintenance")
        grp_maint.setStyleSheet("QGroupBox { color: #f44336; border: 1px solid #552222; }")
        lay_maint = QVBoxLayout()
        self.btn_reset_transaksi = QPushButton("🗑️  Hapus Riwayat Transaksi")
        self.btn_reset_transaksi.clicked.connect(self.reset_transaksi)
        self.btn_vacuum = QPushButton("🧹  Optimize / Vacuum")
        self.btn_vacuum.clicked.connect(self.vacuum_db)
        lay_maint.addWidget(self.btn_reset_transaksi); lay_maint.addWidget(self.btn_vacuum)
        grp_maint.setLayout(lay_maint); layout.addWidget(grp_maint)

        layout.addStretch()
        layout.addWidget(QLabel("Navigasi: Panah & Enter | ESC: Tutup", alignment=Qt.AlignmentFlag.AlignCenter, objectName="InfoLabel"))

        self.update_db_info()
        self.installEventFilter(self)
        self.btn_backup.setFocus()

        # Pasang Event Filter ke semua tombol
        for btn in [self.btn_backup, self.btn_restore, self.btn_export, self.btn_import, self.btn_reset_transaksi, self.btn_vacuum]:
            btn.installEventFilter(self)

    # --- LOGIKA NAVIGASI ---
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape: self.close(); return True
            
            # Navigasi Antar Tombol
            if obj == self.btn_backup:
                if event.key() == Qt.Key.Key_Down: self.btn_restore.setFocus(); return True
            elif obj == self.btn_restore:
                if event.key() == Qt.Key.Key_Up: self.btn_backup.setFocus(); return True
                if event.key() == Qt.Key.Key_Down: self.btn_export.setFocus(); return True
            elif obj == self.btn_export:
                if event.key() == Qt.Key.Key_Right: self.btn_import.setFocus(); return True
                if event.key() == Qt.Key.Key_Up: self.btn_restore.setFocus(); return True
                if event.key() == Qt.Key.Key_Down: self.btn_reset_transaksi.setFocus(); return True
            elif obj == self.btn_import:
                if event.key() == Qt.Key.Key_Left: self.btn_export.setFocus(); return True
                if event.key() == Qt.Key.Key_Up: self.btn_restore.setFocus(); return True
                if event.key() == Qt.Key.Key_Down: self.btn_reset_transaksi.setFocus(); return True
            elif obj == self.btn_reset_transaksi:
                if event.key() == Qt.Key.Key_Up: self.btn_export.setFocus(); return True
                if event.key() == Qt.Key.Key_Down: self.btn_vacuum.setFocus(); return True
            elif obj == self.btn_vacuum:
                if event.key() == Qt.Key.Key_Up: self.btn_reset_transaksi.setFocus(); return True
                
            # Enter Klik Tombol
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                obj.click(); return True

        return super().eventFilter(obj, event)

    # --- FITUR BACKUP (KE FOLDER data/backup) ---
    def backup_db(self):
        # Tentukan folder data/backup
        folder_data = os.path.dirname(DB_PATH)
        folder_backup = os.path.join(folder_data, "backup")
        
        if not os.path.exists(folder_backup):
            os.makedirs(folder_backup)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_pos_{timestamp}.db"
        dest_path = os.path.join(folder_backup, filename)
        
        try:
            shutil.copy(DB_PATH, dest_path)
            QMessageBox.information(self, "Sukses", f"Backup tersimpan rapi di:\n{dest_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal backup: {e}")

    # --- FITUR EXPORT CSV (KE FOLDER data/export) ---
    def export_csv(self):
        # Tentukan folder data/export
        folder_data = os.path.dirname(DB_PATH)
        folder_export = os.path.join(folder_data, "export")
        
        if not os.path.exists(folder_export):
            os.makedirs(folder_export)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"produk_export_{timestamp}.csv"
        # Path default untuk dialog save
        default_path = os.path.join(folder_export, filename)

        # Buka dialog save, arahkan default ke folder export
        save_path, _ = QFileDialog.getSaveFileName(self, "Simpan CSV", default_path, "CSV Files (*.csv)")
        
        if save_path:
            try:
                # Panggil fungsi database dengan path yang dipilih user
                conn = create_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id, barcode, nama, harga, stok FROM produk")
                rows = cursor.fetchall()
                conn.close()

                import csv
                with open(save_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["id", "barcode", "nama", "harga", "stok"])
                    writer.writerows(rows)

                QMessageBox.information(self, "Berhasil", f"Data berhasil diexport ke:\n{save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal export: {str(e)}")

    # --- FITUR LAINNYA ---
    def update_db_info(self):
        if DB_PATH.exists():
            size_kb = os.path.getsize(DB_PATH) / 1024
            self.lbl_size.setText(f"Ukuran: {size_kb:.2f} KB")
        else:
            self.lbl_size.setText("Database Tidak Ditemukan")

    def restore_db(self):
        # Default buka folder backup saat cari file
        folder_data = os.path.dirname(DB_PATH)
        folder_backup = os.path.join(folder_data, "backup")
        if not os.path.exists(folder_backup): folder_backup = folder_data

        file_path, _ = QFileDialog.getOpenFileName(self, "Pilih File Backup", folder_backup, "Database Files (*.db)")
        if not file_path: return

        reply = QMessageBox.question(self, "Restore Database", "Yakin ingin restore? Data saat ini akan ditimpa.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                shutil.copy(file_path, DB_PATH)
                QMessageBox.information(self, "Berhasil", "Database berhasil dipulihkan. Aplikasi akan restart.")
                import sys; sys.exit()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal restore: {e}")

    def reset_transaksi(self):
        reply = QMessageBox.question(self, "Hapus Riwayat", "Hapus SEMUA data transaksi? Produk & User aman.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = create_connection()
            try:
                conn.execute("DELETE FROM detail_transaksi")
                conn.execute("DELETE FROM transaksi")
                conn.execute("DELETE FROM sqlite_sequence WHERE name='transaksi'")
                conn.commit()
                QMessageBox.information(self, "Selesai", "Riwayat transaksi dihapus.")
                self.update_db_info()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
            finally:
                conn.close()

    def vacuum_db(self):
        conn = create_connection()
        try:
            conn.execute("VACUUM"); conn.close()
            QMessageBox.information(self, "Selesai", "Database dioptimalkan.")
            self.update_db_info()
        except Exception as e:
            conn.close(); QMessageBox.critical(self, "Error", str(e))

    def import_csv(self):
        # Default buka folder export saat cari file csv (biar gampang restore)
        folder_data = os.path.dirname(DB_PATH)
        folder_export = os.path.join(folder_data, "export")
        if not os.path.exists(folder_export): folder_export = ""

        path, _ = QFileDialog.getOpenFileName(self, "Pilih CSV", folder_export, "CSV Files (*.csv)")
        if path:
            try:
                import_produk_dari_csv(path)
                QMessageBox.information(self, "Berhasil", "Data produk berhasil diimpor.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def set_current_user(self, username):
        self.current_user = username