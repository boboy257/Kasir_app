from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QPushButton, QLabel,
    QFileDialog, QGroupBox, QHBoxLayout, QFrame
)
from PyQt6.QtCore import Qt
import shutil
import os
from datetime import datetime

from src.ui.base.base_window import BaseWindow
from src.ui.base.style_manager import StyleManager
from src.database import (
    DB_PATH, export_produk_ke_csv, import_produk_dari_csv, 
    create_connection
)


class KelolaDBWindow(BaseWindow):
    
    def __init__(self):
        super().__init__()
        
        self.setup_ui()
        self.setup_navigation()
        
        self.setWindowTitle("Pusat Kontrol Database")
        self.setGeometry(100, 100, 600, 550)
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # Info Database
        info_frame = QFrame()
        info_frame.setStyleSheet(
            "background-color: #181818; border-radius: 5px; border: 1px solid #333;"
        )
        info_layout = QHBoxLayout(info_frame)
        
        self.lbl_path = QLabel(f"Lokasi: ...{str(DB_PATH)[-35:]}")
        self.lbl_size = QLabel("Ukuran: - KB")
        self.lbl_size.setStyleSheet("color: #4CAF50; font-weight: bold;")
        
        info_layout.addWidget(self.lbl_path)
        info_layout.addStretch()
        info_layout.addWidget(self.lbl_size)
        
        layout.addWidget(info_frame)
        
        # Backup & Restore Group
        grp_backup = QGroupBox("Backup & Pemulihan")
        grp_backup.setStyleSheet(
            "QGroupBox { border: 1px solid #333; border-radius: 5px; "
            "margin-top: 10px; font-weight: bold; color: #2196F3; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }"
        )
        
        lay_backup = QVBoxLayout()
        
        style = StyleManager()
        
        self.btn_backup = QPushButton("💾  Backup Database")
        self.btn_backup.clicked.connect(self.backup_db)
        
        self.btn_restore = QPushButton("♻️  Restore Database")
        self.btn_restore.clicked.connect(self.restore_db)
        
        lay_backup.addWidget(self.btn_backup)
        lay_backup.addWidget(self.btn_restore)
        grp_backup.setLayout(lay_backup)
        layout.addWidget(grp_backup)
        
        # Import Export Group
        grp_data = QGroupBox("Migrasi Data Produk")
        grp_data.setStyleSheet(
            "QGroupBox { border: 1px solid #333; border-radius: 5px; "
            "margin-top: 10px; font-weight: bold; color: #2196F3; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }"
        )
        
        lay_data = QHBoxLayout()
        
        self.btn_export = QPushButton("📤 Export CSV")
        self.btn_export.clicked.connect(self.export_csv)
        
        self.btn_import = QPushButton("📥 Import CSV")
        self.btn_import.clicked.connect(self.import_csv)
        
        lay_data.addWidget(self.btn_export)
        lay_data.addWidget(self.btn_import)
        grp_data.setLayout(lay_data)
        layout.addWidget(grp_data)
        
        # Maintenance Group
        grp_maint = QGroupBox("Maintenance")
        grp_maint.setStyleSheet(
            "QGroupBox { color: #f44336; border: 1px solid #552222; "
            "border-radius: 5px; margin-top: 10px; font-weight: bold; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }"
        )
        
        lay_maint = QVBoxLayout()
        
        self.btn_reset_transaksi = QPushButton("🗑️  Hapus Riwayat Transaksi")
        self.btn_reset_transaksi.setStyleSheet(style.get_button_style('danger'))
        self.btn_reset_transaksi.clicked.connect(self.reset_transaksi)
        
        self.btn_vacuum = QPushButton("🧹  Optimize / Vacuum")
        self.btn_vacuum.clicked.connect(self.vacuum_db)
        
        lay_maint.addWidget(self.btn_reset_transaksi)
        lay_maint.addWidget(self.btn_vacuum)
        grp_maint.setLayout(lay_maint)
        layout.addWidget(grp_maint)
        
        layout.addStretch()
        
        lbl_nav = QLabel("Arrow & Enter | ESC=Close")
        lbl_nav.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_nav.setStyleSheet("font-size: 11px; color: #777; font-style: italic;")
        layout.addWidget(lbl_nav)
        
        self.update_db_info()
        self.btn_backup.setFocus()
    
    def setup_navigation(self):
        """Grid-style navigation untuk button layout"""
        # Vertical navigation (Down/Up)
        self.register_navigation(self.btn_backup, {
            Qt.Key.Key_Down: self.btn_restore,
            Qt.Key.Key_Return: self.backup_db
        })
        
        self.register_navigation(self.btn_restore, {
            Qt.Key.Key_Up: self.btn_backup,
            Qt.Key.Key_Down: self.btn_export,
            Qt.Key.Key_Return: self.restore_db
        })
        
        # Import/Export row (horizontal)
        self.register_navigation(self.btn_export, {
            Qt.Key.Key_Up: self.btn_restore,
            Qt.Key.Key_Right: self.btn_import,
            Qt.Key.Key_Down: self.btn_reset_transaksi,
            Qt.Key.Key_Return: self.export_csv
        })
        
        self.register_navigation(self.btn_import, {
            Qt.Key.Key_Up: self.btn_restore,
            Qt.Key.Key_Left: self.btn_export,
            Qt.Key.Key_Down: self.btn_reset_transaksi,
            Qt.Key.Key_Return: self.import_csv
        })
        
        # Maintenance buttons
        self.register_navigation(self.btn_reset_transaksi, {
            Qt.Key.Key_Up: self.btn_export,
            Qt.Key.Key_Down: self.btn_vacuum,
            Qt.Key.Key_Return: self.reset_transaksi
        })
        
        self.register_navigation(self.btn_vacuum, {
            Qt.Key.Key_Up: self.btn_reset_transaksi,
            Qt.Key.Key_Return: self.vacuum_db
        })
    
    def update_db_info(self):
        """Update database info display"""
        if DB_PATH.exists():
            size_kb = os.path.getsize(DB_PATH) / 1024
            self.lbl_size.setText(f"Ukuran: {size_kb:.2f} KB")
        else:
            self.lbl_size.setText("Database Tidak Ditemukan")
    
    def backup_db(self):
        """Backup database ke folder data/backup"""
        folder_data = os.path.dirname(DB_PATH)
        folder_backup = os.path.join(folder_data, "backup")
        
        if not os.path.exists(folder_backup):
            os.makedirs(folder_backup)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_pos_{timestamp}.db"
        dest_path = os.path.join(folder_backup, filename)
        
        try:
            shutil.copy(DB_PATH, dest_path)
            self.show_success("Sukses", f"Backup tersimpan rapi di:\n{dest_path}")
            self.update_db_info()
        except Exception as e:
            self.show_error("Error", f"Gagal backup: {e}")
    
    def restore_db(self):
        """Restore database from backup"""
        folder_data = os.path.dirname(DB_PATH)
        folder_backup = os.path.join(folder_data, "backup")
        
        if not os.path.exists(folder_backup):
            folder_backup = folder_data
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih File Backup", folder_backup, "Database Files (*.db)"
        )
        
        if not file_path:
            return
        
        if not self.confirm_action(
            "Restore Database",
            "Yakin ingin restore? Data saat ini akan ditimpa."
        ):
            return
        
        try:
            shutil.copy(file_path, DB_PATH)
            self.show_success(
                "Berhasil",
                "Database berhasil dipulihkan. Aplikasi akan restart."
            )
            import sys
            sys.exit()
        except Exception as e:
            self.show_error("Error", f"Gagal restore: {e}")
    
    def export_csv(self):
        """Export produk ke CSV"""
        folder_data = os.path.dirname(DB_PATH)
        folder_export = os.path.join(folder_data, "export")
        
        if not os.path.exists(folder_export):
            os.makedirs(folder_export)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"produk_export_{timestamp}.csv"
        default_path = os.path.join(folder_export, filename)
        
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Simpan CSV", default_path, "CSV Files (*.csv)"
        )
        
        if not save_path:
            return
        
        try:
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
            
            self.show_success("Berhasil", f"Data berhasil diexport ke:\n{save_path}")
            
        except Exception as e:
            self.show_error("Error", f"Gagal export: {str(e)}")
    
    def import_csv(self):
        """Import produk dari CSV"""
        folder_data = os.path.dirname(DB_PATH)
        folder_export = os.path.join(folder_data, "export")
        
        if not os.path.exists(folder_export):
            folder_export = ""
        
        path, _ = QFileDialog.getOpenFileName(
            self, "Pilih CSV", folder_export, "CSV Files (*.csv)"
        )
        
        if not path:
            return
        
        try:
            import_produk_dari_csv(path)
            self.show_success("Berhasil", "Data produk berhasil diimpor.")
        except Exception as e:
            self.show_error("Error", str(e))
    
    def reset_transaksi(self):
        """Hapus semua riwayat transaksi"""
        if not self.confirm_action(
            "Hapus Riwayat",
            "Hapus SEMUA data transaksi? Produk & User aman."
        ):
            return
        
        conn = create_connection()
        try:
            conn.execute("DELETE FROM detail_transaksi")
            conn.execute("DELETE FROM transaksi")
            conn.execute("DELETE FROM sqlite_sequence WHERE name='transaksi'")
            conn.commit()
            
            self.show_success("Selesai", "Riwayat transaksi dihapus.")
            self.update_db_info()
            
        except Exception as e:
            self.show_error("Error", str(e))
        finally:
            conn.close()
    
    def vacuum_db(self):
        """Optimize database"""
        conn = create_connection()
        try:
            conn.execute("VACUUM")
            conn.close()
            
            self.show_success("Selesai", "Database dioptimalkan.")
            self.update_db_info()
            
        except Exception as e:
            conn.close()
            self.show_error("Error", str(e))