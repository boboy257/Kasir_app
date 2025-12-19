"""
Log Aktivitas Window - SmartNavigation
=======================================
Audit trail dengan filter + table
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel, 
    QComboBox, QDateEdit, QLineEdit, QFrame, QFileDialog
)
from PyQt6.QtCore import Qt, QDate, QEvent
import csv

from src.ui.base.base_window import BaseWindow
from src.ui.base.style_manager import StyleManager
from src.ui.widgets.smart_table import SmartTable
from src.database import ambil_log_aktivitas, semua_user


class LogAktivitasWindow(BaseWindow):
    """Audit trail window"""
    
    def __init__(self):
        super().__init__()
        
        self.setup_ui()
        self.setup_navigation()
        
        self.setWindowTitle("Audit Trail / Log Aktivitas")
        self.setGeometry(100, 100, 1100, 700)
        
        self.muat_log()
    
    def setup_ui(self):
        """Setup UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Filter frame
        filter_frame = QFrame()
        filter_frame.setStyleSheet(
            "background-color: #181818; border-radius: 8px; border: 1px solid #333;"
        )
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(15, 15, 15, 15)
        filter_layout.setSpacing(10)
        
        # Date filters
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDisplayFormat("yyyy-MM-dd")
        self.date_start.setDate(QDate.currentDate().addDays(-7))
        self.date_start.setFixedWidth(110)
        
        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDisplayFormat("yyyy-MM-dd")
        self.date_end.setDate(QDate.currentDate())
        self.date_end.setFixedWidth(110)
        
        # User filter
        self.combo_user = QComboBox()
        self.combo_user.setMinimumWidth(150)
        self.isi_combo_user()
        
        # Search keyword
        self.input_cari = QLineEdit()
        self.input_cari.setPlaceholderText("Cari aktivitas... (Ctrl+F)")
        
        # Filter button
        style = StyleManager()
        
        self.btn_filter = QPushButton("Terapkan Filter")
        self.btn_filter.setStyleSheet(style.get_button_style('primary'))
        self.btn_filter.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_filter.clicked.connect(self.muat_log)
        
        # Export button
        self.btn_export = QPushButton("Export CSV")
        self.btn_export.setStyleSheet(style.get_button_style('success'))
        self.btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export.clicked.connect(self.export_csv)
        
        # Layout filters
        filter_layout.addWidget(QLabel("Tgl:"))
        filter_layout.addWidget(self.date_start)
        filter_layout.addWidget(QLabel("-"))
        filter_layout.addWidget(self.date_end)
        filter_layout.addWidget(QLabel("User:"))
        filter_layout.addWidget(self.combo_user)
        filter_layout.addWidget(QLabel("Cari:"))
        filter_layout.addWidget(self.input_cari)
        filter_layout.addWidget(self.btn_filter)
        filter_layout.addWidget(self.btn_export)
        
        layout.addWidget(filter_frame)
        
        # Table
        self.table_log = SmartTable(0, 4)
        self.table_log.setHorizontalHeaderLabels(["Waktu", "User", "Aktivitas", "Detail"])
        self.table_log.stretch_column(3)
        self.table_log.set_column_width(0, 150)
        self.table_log.set_column_width(1, 100)
        self.table_log.set_column_width(2, 150)
        
        layout.addWidget(self.table_log)
        
        # Footer
        footer_layout = QHBoxLayout()
        
        lbl_legend = QLabel(
            "Keterangan: "
            "<span style='color:#00E5FF'>■ Transaksi</span> &nbsp; "
            "<span style='color:#4CAF50'>■ Tambah</span> &nbsp; "
            "<span style='color:#FFC107'>■ Edit</span> &nbsp; "
            "<span style='color:#F44336'>■ Hapus</span>"
        )
        lbl_legend.setTextFormat(Qt.TextFormat.RichText)
        footer_layout.addWidget(lbl_legend)
        
        footer_layout.addStretch()
        
        lbl_nav = QLabel("Ctrl+←→ = Skip Date | ↑↓ = Table | Space = Open User | Enter = Filter | ESC = Close")
        lbl_nav.setStyleSheet("color: #777; font-size: 11px; font-style: italic;")
        footer_layout.addWidget(lbl_nav)
        
        layout.addLayout(footer_layout)
        
        self.date_start.setFocus()
    
    def setup_navigation(self):
        """
        Filter row (horizontal Left/Right) → Table (vertical Up/Down)
        """
        # Filter row - horizontal navigation
        self.register_navigation(self.date_start, {
            # Qt.Key.Key_Right: self.date_end,
            Qt.Key.Key_Return: self.date_end,
            Qt.Key.Key_Down: lambda: self.focus_table_first_row(self.table_log)
        })
        
        self.register_navigation(self.date_end, {
            Qt.Key.Key_Left: self.date_start,
            # Qt.Key.Key_Right: self.combo_user,
            Qt.Key.Key_Return: self.combo_user,
            Qt.Key.Key_Down: lambda: self.focus_table_first_row(self.table_log)
        })
        
        self.register_navigation(self.combo_user, {
            Qt.Key.Key_Left: self.date_end,
            Qt.Key.Key_Right: self.input_cari,
            Qt.Key.Key_Return: self.input_cari,
            Qt.Key.Key_Space: lambda: self.combo_user.showPopup(),
            Qt.Key.Key_Down: lambda: self.focus_table_first_row(self.table_log)
        })
        
        self.register_navigation(self.input_cari, {
            Qt.Key.Key_Left: self.combo_user,
            Qt.Key.Key_Right: self.btn_filter,
            Qt.Key.Key_Return: lambda: (self.muat_log(), self.btn_filter.setFocus()),
            Qt.Key.Key_Down: lambda: (self.combo_user.showPopup(), None)[1] or self.focus_table_first_row(self.table_log)
        })
        
        self.register_navigation(self.btn_filter, {
            Qt.Key.Key_Left: self.input_cari,
            Qt.Key.Key_Right: self.btn_export,
            Qt.Key.Key_Return: self.muat_log,
            Qt.Key.Key_Down: lambda: self.focus_table_first_row(self.table_log)
        })
        
        self.register_navigation(self.btn_export, {
            Qt.Key.Key_Left: self.btn_filter,
            Qt.Key.Key_Right: self.date_start,  # Circular
            Qt.Key.Key_Return: self.export_csv,
            Qt.Key.Key_Down: lambda: self.focus_table_first_row(self.table_log)
        })
        
        # Table: Up dari row 0 → input_cari
        self.register_table_callbacks(self.table_log, {
            'focus_up': self.input_cari,
            'focus_down': self.btn_filter
        })
    
    # def eventFilter(self, obj, event):
    #     """Override untuk handle QDateEdit navigation"""
    #     if event.type() == QEvent.Type.KeyPress:
    #         key = event.key()
            
    #         # QDateEdit: Ctrl+Right untuk skip ke field berikutnya
    #         if obj == self.date_start:
    #             if key == Qt.Key.Key_Right and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
    #                 self.date_end.setFocus()
    #                 return True
            
    #         if obj == self.date_end:
    #             if key == Qt.Key.Key_Right and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
    #                 self.combo_user.setFocus()
    #                 return True
    #             if key == Qt.Key.Key_Left and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
    #                 self.date_start.setFocus()
    #                 return True
        
    #     return super().eventFilter(obj, event)
    
    def isi_combo_user(self):
        """Populate user combo"""
        self.combo_user.clear()
        self.combo_user.addItem("Semua Pengguna", None)
        
        user_list = semua_user()
        for id_user, username, role in user_list:
            self.combo_user.addItem(username, username)
    
    def muat_log(self):
        """Load activity log"""
        self.table_log.clear_table()
        
        user_filter = self.combo_user.currentData()
        keyword = self.input_cari.text().strip()
        start_date = self.date_start.date().toString("yyyy-MM-dd")
        end_date = self.date_end.date().toString("yyyy-MM-dd")
        
        log_list = ambil_log_aktivitas(
            username=user_filter,
            keyword=keyword,
            start_date=start_date,
            end_date=end_date
        )
        
        from PyQt6.QtWidgets import QTableWidgetItem
        
        for row, (username, aktivitas, tanggal, detail) in enumerate(log_list):
            self.table_log.insertRow(row)
            self.table_log.setItem(row, 0, QTableWidgetItem(tanggal))
            self.table_log.setItem(row, 1, QTableWidgetItem(username))
            
            # Color-coded activity
            item_akt = QTableWidgetItem(aktivitas)
            
            if "Hapus" in aktivitas:
                item_akt.setForeground(Qt.GlobalColor.red)
            elif "Edit" in aktivitas or "Update" in aktivitas:
                item_akt.setForeground(Qt.GlobalColor.yellow)
            elif "Tambah" in aktivitas:
                item_akt.setForeground(Qt.GlobalColor.green)
            elif "Transaksi" in aktivitas:
                item_akt.setForeground(Qt.GlobalColor.cyan)
            else:
                item_akt.setForeground(Qt.GlobalColor.white)
            
            self.table_log.setItem(row, 2, item_akt)
            self.table_log.setItem(row, 3, QTableWidgetItem(detail if detail else "-"))
    
    def export_csv(self):
        """Export log to CSV"""
        if self.table_log.rowCount() == 0:
            self.show_warning("Tidak Ada Data", "Tidak ada log untuk diexport.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Simpan Log", "log_aktivitas.csv", "CSV (*.csv)"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Waktu", "User", "Aktivitas", "Detail"])
                
                for row in range(self.table_log.rowCount()):
                    writer.writerow([
                        self.table_log.item(row, 0).text(),
                        self.table_log.item(row, 1).text(),
                        self.table_log.item(row, 2).text(),
                        self.table_log.item(row, 3).text()
                    ])
            
            self.show_success("Berhasil", f"Log disimpan:\n{filename}")
            
        except Exception as e:
            self.show_error("Error", str(e))