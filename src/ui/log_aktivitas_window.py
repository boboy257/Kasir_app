from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLabel, QComboBox, QHeaderView, QAbstractItemView,
    QDateEdit, QLineEdit, QFrame, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QEvent, QDate
from src.database import ambil_log_aktivitas, semua_user
import csv

class LogAktivitasWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audit Trail / Log Aktivitas")
        self.setGeometry(100, 100, 1100, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # --- STYLE DARK MODE & TOMBOL BESAR ---
        self.setStyleSheet("""
            QWidget { 
                background-color: #121212; color: #e0e0e0; 
                font-family: 'Segoe UI', sans-serif; font-size: 13px; outline: none;
            }
            
            QLineEdit, QComboBox, QDateEdit { 
                background-color: #1E1E1E; border: 1px solid #333; 
                padding: 8px; color: white; border-radius: 4px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus { 
                border: 2px solid #2196F3; background-color: #263238; 
            }

            QTableWidget { 
                background-color: #1E1E1E; gridline-color: #333; 
                border: 1px solid #333; border-radius: 5px;
            }
            QTableWidget:focus { border: 2px solid #2196F3; }
            QHeaderView::section { 
                background-color: #252525; color: white; 
                padding: 8px; border: none; font-weight: bold; 
            }
            QTableWidget::item:selected { background-color: #2196F3; color: white; }

            /* [PERBAIKAN] TOMBOL LEGA (Sama seperti Stok Rendah) */
            QPushButton { 
                background-color: #1E1E1E; 
                border: 1px solid #555; 
                padding: 10px 20px; /* Padding Besar */
                min-height: 30px;   /* Tinggi Minimal Aman */
                border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #333; }
            QPushButton:focus { 
                border: 2px solid #ffffff; /* Fokus Putih Jelas */
                background-color: #424242; 
            }
            
            QLabel { font-weight: bold; color: #bbb; }
        """)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # --- 1. FILTER AREA ---
        filter_frame = QFrame()
        filter_frame.setStyleSheet("background-color: #181818; border-radius: 8px; border: 1px solid #333;")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(15, 15, 15, 15)
        filter_layout.setSpacing(10)

        # Tanggal
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDisplayFormat("yyyy-MM-dd")
        self.date_start.setDate(QDate.currentDate().addDays(-7)) 
        self.date_start.setFixedWidth(110)
        self.date_start.installEventFilter(self)

        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDisplayFormat("yyyy-MM-dd")
        self.date_end.setDate(QDate.currentDate())
        self.date_end.setFixedWidth(110)
        self.date_end.installEventFilter(self)

        # User Combo
        self.combo_user = QComboBox()
        self.combo_user.setMinimumWidth(150)
        self.isi_combo_user()
        self.combo_user.installEventFilter(self)

        # Search Keyword
        self.input_cari = QLineEdit()
        self.input_cari.setPlaceholderText("Cari aktivitas (misal: 'Hapus')...")
        self.input_cari.installEventFilter(self)

        # Tombol Filter (Biru)
        self.btn_filter = QPushButton("Terapkan Filter")
        self.btn_filter.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_filter.setStyleSheet("""
            QPushButton { background-color: #2196F3; color: white; border: none; }
            QPushButton:hover { background-color: #1976D2; }
            QPushButton:focus { border: 2px solid #fff; }
        """)
        self.btn_filter.clicked.connect(self.muat_log)
        self.btn_filter.installEventFilter(self)
        
        # Tombol Export (Hijau)
        self.btn_export = QPushButton("Export CSV")
        self.btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export.setStyleSheet("""
            QPushButton { border: 1px solid #4CAF50; color: #4CAF50; }
            QPushButton:focus { border: 2px solid #fff; background-color: #1B5E20; color: white; }
        """)
        self.btn_export.clicked.connect(self.export_csv)
        self.btn_export.installEventFilter(self)

        # Layout Filter
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

        # --- 2. TABEL LOG ---
        self.table_log = QTableWidget(0, 4)
        self.table_log.setHorizontalHeaderLabels(["Waktu", "User", "Aktivitas", "Detail"])
        self.table_log.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_log.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_log.setAlternatingRowColors(True)
        self.table_log.setStyleSheet("QTableWidget { alternate-background-color: #252525; }")
        
        header = self.table_log.horizontalHeader()
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch) # Detail melar
        self.table_log.setColumnWidth(0, 150) # Waktu
        self.table_log.setColumnWidth(1, 100) # User
        self.table_log.setColumnWidth(2, 150) # Aktivitas
        
        self.table_log.installEventFilter(self)
        layout.addWidget(self.table_log)
        
        # --- 3. FOOTER (LEGEND & INFO) ---
        footer_layout = QHBoxLayout()
        
        # Legend Warna
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
        
        lbl_nav = QLabel("Navigasi: Enter/Tab (Pindah Kolom) | ESC (Tutup)", styleSheet="color: #777; font-size: 11px; font-style: italic;")
        footer_layout.addWidget(lbl_nav)
        
        layout.addLayout(footer_layout)

        # Muat Data Awal
        self.muat_log()
        self.date_start.setFocus() 

        self.installEventFilter(self)

    # --- LOGIKA NAVIGASI KEYBOARD ---
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            
            # GLOBAL ESC
            if event.key() == Qt.Key.Key_Escape: self.close(); return True
            
            # 1. TANGGAL (Hanya Enter yang pindah widget, Panah dibiarkan untuk edit tanggal)
            if obj == self.date_start:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.date_end.setFocus(); return True
            
            elif obj == self.date_end:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.combo_user.setFocus(); return True

            # 2. COMBO USER
            elif obj == self.combo_user:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.input_cari.setFocus(); return True
                # Kanan/Kiri untuk pindah widget (karena combo box pakai Atas/Bawah buat pilih)
                elif event.key() == Qt.Key.Key_Right: self.input_cari.setFocus(); return True
                elif event.key() == Qt.Key.Key_Left: self.date_end.setFocus(); return True

            # 3. INPUT CARI
            elif obj == self.input_cari:
                # Enter -> Langsung Filter (Klik tombol)
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.btn_filter.click(); self.btn_filter.setFocus(); return True
                elif event.key() == Qt.Key.Key_Right: self.btn_filter.setFocus(); return True
                elif event.key() == Qt.Key.Key_Left: self.combo_user.setFocus(); return True
                elif event.key() == Qt.Key.Key_Down: self.table_log.setFocus(); return True

            # 4. TOMBOL FILTER
            elif obj == self.btn_filter:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.btn_filter.click(); return True
                elif event.key() == Qt.Key.Key_Right: self.btn_export.setFocus(); return True
                elif event.key() == Qt.Key.Key_Left: self.input_cari.setFocus(); return True
                elif event.key() == Qt.Key.Key_Down: self.table_log.setFocus(); return True

            # 5. TOMBOL EXPORT
            elif obj == self.btn_export:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.btn_export.click(); return True
                elif event.key() == Qt.Key.Key_Left: self.btn_filter.setFocus(); return True
                elif event.key() == Qt.Key.Key_Down: self.table_log.setFocus(); return True

            # 6. TABEL
            elif obj == self.table_log:
                if event.key() == Qt.Key.Key_Up and self.table_log.currentRow() <= 0:
                    self.input_cari.setFocus()
                    return True

        return super().eventFilter(obj, event)

    def isi_combo_user(self):
        self.combo_user.clear()
        self.combo_user.addItem("Semua Pengguna", None)
        user_list = semua_user()
        for id_user, username, role in user_list:
            self.combo_user.addItem(username, username)

    def muat_log(self):
        self.table_log.setRowCount(0)
        
        user_filter = self.combo_user.currentData()
        keyword = self.input_cari.text().strip()
        start_date = self.date_start.date().toString("yyyy-MM-dd")
        end_date = self.date_end.date().toString("yyyy-MM-dd")
        
        log_list = ambil_log_aktivitas(username=user_filter, keyword=keyword, start_date=start_date, end_date=end_date)
        
        for row, (username, aktivitas, tanggal, detail) in enumerate(log_list):
            self.table_log.insertRow(row)
            self.table_log.setItem(row, 0, QTableWidgetItem(tanggal))
            self.table_log.setItem(row, 1, QTableWidgetItem(username))
            
            # --- COLOR CODING ---
            item_akt = QTableWidgetItem(aktivitas)
            item_akt.setFont(self.font())
            
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
        if self.table_log.rowCount() == 0: return
        
        filename, _ = QFileDialog.getSaveFileName(self, "Simpan Log", "log_aktivitas.csv", "CSV (*.csv)")
        if filename:
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
                QMessageBox.information(self, "Berhasil", f"Log disimpan:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def set_current_user(self, username):
        self.current_user = username