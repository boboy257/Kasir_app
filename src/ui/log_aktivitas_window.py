from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLabel, QComboBox, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, QEvent # [TAMBAHAN] Import QEvent
from src.database import ambil_log_aktivitas, semua_user

class LogAktivitasWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Log Aktivitas Pengguna")
        self.setGeometry(100, 100, 1000, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # --- STYLE DARK MODE ---
        central_widget.setStyleSheet("""
            QWidget { background-color: #121212; color: #e0e0e0; font-family: 'Segoe UI'; font-size: 13px; outline: none; }
            QComboBox { background-color: #1E1E1E; border: 1px solid #333; padding: 5px; color: white; }
            QComboBox:focus { border: 2px solid #2196F3; }
            QTableWidget { background-color: #1E1E1E; gridline-color: #333; border: 1px solid #333; }
            QHeaderView::section { background-color: #252525; color: white; padding: 8px; border: none; font-weight: bold; }
            QPushButton { background-color: #2196F3; color: white; border: none; padding: 8px 15px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #1976D2; }
            QPushButton:focus { border: 2px solid #ffffff; }
            QLabel { font-weight: bold; color: #bbb; }
        """)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)

        # Filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter Pengguna:"))
        
        self.combo_user = QComboBox()
        self.combo_user.setMinimumWidth(200)
        self.combo_user.addItem("Semua Pengguna", None)
        self.isi_combo_user()
        self.combo_user.currentIndexChanged.connect(self.muat_log)
        filter_layout.addWidget(self.combo_user)
        
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.muat_log)
        filter_layout.addWidget(self.btn_refresh)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Tabel log
        self.table_log = QTableWidget(0, 4)
        self.table_log.setHorizontalHeaderLabels(["Username", "Aktivitas", "Tanggal", "Detail"])
        self.table_log.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_log.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_log.setAlternatingRowColors(True)
        self.table_log.setStyleSheet("QTableWidget { alternate-background-color: #252525; }")
        
        header = self.table_log.horizontalHeader()
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch) # Detail melar
        
        layout.addWidget(self.table_log)

        self.muat_log()
        
        # [PENTING] Pasang telinga ESC
        self.installEventFilter(self)

    # [LOGIKA ESC]
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Escape:
            self.close()
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
        log_list = ambil_log_aktivitas(username=user_filter)
        
        for row, (username, aktivitas, tanggal, detail) in enumerate(log_list):
            self.table_log.insertRow(row)
            self.table_log.setItem(row, 0, QTableWidgetItem(username))
            self.table_log.setItem(row, 1, QTableWidgetItem(aktivitas))
            self.table_log.setItem(row, 2, QTableWidgetItem(tanggal))
            self.table_log.setItem(row, 3, QTableWidgetItem(detail if detail else "-"))

    def set_current_user(self, username):
        self.current_user = username