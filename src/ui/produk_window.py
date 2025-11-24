from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QHBoxLayout,
    QLineEdit, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox
)
from src.database import tambah_produk, semua_produk

class ProdukWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Input Produk")
        self.setGeometry(100, 100, 900, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Form input produk
        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("Barcode:"))
        self.barcode_input = QLineEdit()
        form_layout.addWidget(self.barcode_input)

        form_layout.addWidget(QLabel("Nama:"))
        self.nama_input = QLineEdit()
        form_layout.addWidget(self.nama_input)

        form_layout.addWidget(QLabel("Harga:"))
        self.harga_input = QLineEdit()
        form_layout.addWidget(self.harga_input)

        form_layout.addWidget(QLabel("Stok:"))
        self.stok_input = QLineEdit()
        form_layout.addWidget(self.stok_input)

        layout.addLayout(form_layout)

        self.btn_simpan = QPushButton("Simpan Produk")
        self.btn_simpan.clicked.connect(self.simpan_produk)
        layout.addWidget(self.btn_simpan)

        # Tabel produk
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Barcode", "Nama", "Harga", "Stok"])
        layout.addWidget(self.table)

        self.muat_produk()

    def simpan_produk(self):
        barcode = self.barcode_input.text().strip()
        nama = self.nama_input.text().strip()
        harga = self.harga_input.text().strip()
        stok = self.stok_input.text().strip()

        if not barcode or not nama or not harga:
            QMessageBox.warning(self, "Input Tidak Lengkap", "Lengkapi semua data.")
            return

        try:
            harga = float(harga)
            stok = int(stok) if stok else 0
        except ValueError:
            QMessageBox.warning(self, "Input Salah", "Harga harus angka.")
            return

        tambah_produk(barcode, nama, harga, stok)
        self.muat_produk()

        # Clear form
        self.barcode_input.clear()
        self.nama_input.clear()
        self.harga_input.clear()
        self.stok_input.clear()

    def muat_produk(self):
        self.table.setRowCount(0)
        produk_list = semua_produk()
        for row, (barcode, nama, harga, stok) in enumerate(produk_list):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(barcode))
            self.table.setItem(row, 1, QTableWidgetItem(nama))
            self.table.setItem(row, 2, QTableWidgetItem(f"Rp {harga}"))
            self.table.setItem(row, 3, QTableWidgetItem(str(stok)))