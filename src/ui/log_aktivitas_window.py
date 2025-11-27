from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLabel, QComboBox
)
from src.database import ambil_log_aktivitas, semua_user

class LogAktivitasWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Log Aktivitas Pengguna")
        self.setGeometry(100, 100, 1000, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter Pengguna:"))
        
        self.combo_user = QComboBox()
        self.combo_user.addItem("Semua Pengguna", None)
        # Isi combo box dengan semua user dari database
        self.isi_combo_user()
        self.combo_user.currentIndexChanged.connect(self.muat_log)
        filter_layout.addWidget(self.combo_user)
        
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.muat_log)
        filter_layout.addWidget(self.btn_refresh)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Tabel log
        self.table_log = QTableWidget(0, 4)
        self.table_log.setHorizontalHeaderLabels(["Username", "Aktivitas", "Tanggal", "Detail"])
        layout.addWidget(self.table_log)

        # Muat data awal
        self.muat_log()

    def isi_combo_user(self):
        """Isi combo box dengan semua user dari database"""
        # Bersihkan combo box dulu
        self.combo_user.clear()
        
        # Tambahkan "Semua Pengguna"
        self.combo_user.addItem("Semua Pengguna", None)
        
        # Ambil semua user dari database
        user_list = semua_user()
        
        # Tambahkan setiap user ke combo box
        for id_user, username in user_list:
            self.combo_user.addItem(username, username)

    def muat_log(self):
        """Muat log aktivitas ke tabel"""
        self.table_log.setRowCount(0)
        
        # Ambil filter user
        user_filter = self.combo_user.currentData()
        
        log_list = ambil_log_aktivitas(username=user_filter)

        print(f"Debug - Jumlah log ditemukan: {len(log_list)}")
        
        for row, (username, aktivitas, tanggal, detail) in enumerate(log_list):
            self.table_log.insertRow(row)
            self.table_log.setItem(row, 0, QTableWidgetItem(username))
            self.table_log.setItem(row, 1, QTableWidgetItem(aktivitas))
            self.table_log.setItem(row, 2, QTableWidgetItem(tanggal))
            self.table_log.setItem(row, 3, QTableWidgetItem(detail if detail else "-"))

    def set_current_user(self, username):
        """Set username untuk window ini"""
        self.current_user = username