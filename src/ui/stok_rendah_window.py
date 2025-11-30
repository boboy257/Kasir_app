from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLabel
)
from src.database import create_connection

class StokRendahWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Laporan Stok Rendah")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Label info
        label_info = QLabel("Produk dengan stok di bawah 5:")
        layout.addWidget(label_info)

        # Tombol refresh
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh Data")
        self.btn_refresh.clicked.connect(self.muat_stok_rendah)
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Tabel laporan stok rendah
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Barcode", "Nama", "Stok"])
        layout.addWidget(self.table)

        # Muat data awal
        self.muat_stok_rendah()

    def muat_stok_rendah(self):
        """Muat produk dengan stok rendah (stok < 5)"""
        # Kosongkan tabel
        self.table.setRowCount(0)

        # Ambil data dari database
        conn = create_connection()
        cursor = conn.cursor()

        # Query untuk ambil produk dengan stok rendah
        cursor.execute("""
            SELECT id, barcode, nama, stok 
            FROM produk 
            WHERE stok < 5 
            ORDER BY stok ASC
        """)
        hasil = cursor.fetchall()
        conn.close()

        # Isi tabel
        for row, (id_produk, barcode, nama, stok) in enumerate(hasil):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(id_produk)))
            self.table.setItem(row, 1, QTableWidgetItem(barcode))
            self.table.setItem(row, 2, QTableWidgetItem(nama))
            self.table.setItem(row, 3, QTableWidgetItem(str(stok)))
            
    def set_current_user(self, username):
        self.current_user = username