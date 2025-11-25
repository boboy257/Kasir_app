from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QHBoxLayout,
    QLineEdit, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QInputDialog 
)
from PyQt6.QtCore import Qt
from src.database import cari_produk_dari_barcode, create_connection
import sqlite3
from datetime import datetime
from src.cetak_struk import cetak_struk_pdf

class KasirWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplikasi Kasir - Mode Penjualan")
        self.setGeometry(100, 100, 900, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Input barcode
        barcode_layout = QHBoxLayout()
        barcode_layout.addWidget(QLabel("Barcode:"))
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Scan barcode di sini...")
        self.barcode_input.returnPressed.connect(self.tambah_barang_ke_keranjang)
        barcode_layout.addWidget(self.barcode_input)
        layout.addLayout(barcode_layout)

        # Tombol scan (opsional, untuk debugging atau jika tidak pakai scanner fisik)
        self.btn_scan = QPushButton("Scan")
        self.btn_scan.clicked.connect(self.scan_barcode_manual)
        barcode_layout.addWidget(self.btn_scan)
        
        layout.addLayout(barcode_layout)

        # Tabel keranjang
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Nama", "Harga", "Jumlah", "Subtotal"])
        layout.addWidget(self.table)

        # Total
        self.label_total = QLabel("Total: Rp 0")
        self.label_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.label_total)

        # Tombol bayar
        btn_layout = QHBoxLayout()
        self.btn_bayar = QPushButton("Bayar")
        self.btn_bayar.clicked.connect(self.bayar)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_bayar)
        layout.addLayout(btn_layout)

        self.keranjang = []
        self.total = 0

    def tambah_barang_ke_keranjang(self):
        barcode = self.barcode_input.text().strip()
        if not barcode:
            return

        produk = cari_produk_dari_barcode(barcode)
        if produk:
            nama, harga = produk
            self.keranjang.append((nama, harga, 1, harga))
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(nama))
            self.table.setItem(row, 1, QTableWidgetItem(f"Rp {harga}"))
            self.table.setItem(row, 2, QTableWidgetItem("1"))
            self.table.setItem(row, 3, QTableWidgetItem(f"Rp {harga}"))

            self.total += harga
            self.label_total.setText(f"Total: Rp {self.total}")
        else:
            QMessageBox.warning(self, "Barang Tidak Ditemukan", f"Barcode {barcode} tidak ditemukan di database.")

        self.barcode_input.clear()

    def scan_barcode_manual(self):
        """Fungsi untuk scan barcode manual (jika tidak pakai scanner fisik)"""
        
        barcode, ok = QInputDialog.getText(
            self, 
            "Input Barcode", 
            "Masukkan barcode produk:"
        )
        
        if ok and barcode:
            self.barcode_input.setText(barcode)
            self.tambah_barang_ke_keranjang()

    def bayar(self):
        if not self.keranjang:
            QMessageBox.information(self, "Keranjang Kosong", "Tambahkan barang ke keranjang terlebih dahulu.")
            return

        conn = create_connection()
        cursor = conn.cursor()

        # Simpan transaksi
        cursor.execute("""
            INSERT INTO transaksi (tanggal, total)
            VALUES (?, ?)
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.total))

        transaksi_id = cursor.lastrowid

        # Simpan detail transaksi
        for nama, harga, jumlah, subtotal in self.keranjang:
            cursor.execute("""
                INSERT INTO detail_transaksi (transaksi_id, produk_nama, jumlah, harga, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (transaksi_id, nama, jumlah, harga, subtotal))

        # Cetak struk
        from src.config import NAMA_TOKO, ALAMAT_TOKO
        cetak_struk_pdf(NAMA_TOKO, ALAMAT_TOKO, self.keranjang, self.total)


        conn.commit()
        conn.close()

        QMessageBox.information(self, "Pembayaran Berhasil", f"Total: Rp {self.total}\nTransaksi berhasil disimpan.")
        self.reset_keranjang()

    def reset_keranjang(self):
        self.keranjang.clear()
        self.total = 0
        self.table.setRowCount(0)
        self.label_total.setText("Total: Rp 0")