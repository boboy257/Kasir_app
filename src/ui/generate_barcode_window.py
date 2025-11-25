from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QHBoxLayout,
    QLineEdit, QLabel, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QFormLayout
)
from PyQt6.QtCore import Qt
from src.database import semua_produk, generate_barcode_gambar, generate_semua_barcode_gambar

class GenerateBarcodeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generate Barcode")
        self.setGeometry(100, 100, 900, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Form untuk generate barcode individual
        form_layout = QFormLayout()
        
        # Input barcode
        self.input_barcode = QLineEdit()
        self.input_barcode.setPlaceholderText("Masukkan barcode produk")
        form_layout.addRow("Barcode:", self.input_barcode)
        
        # Input nama produk
        self.input_nama = QLineEdit()
        self.input_nama.setPlaceholderText("Masukkan nama produk")
        form_layout.addRow("Nama Produk:", self.input_nama)
        
        layout.addLayout(form_layout)

        # Tombol generate
        btn_layout = QHBoxLayout()
        
        self.btn_generate_single = QPushButton("Generate Barcode Individual")
        self.btn_generate_single.clicked.connect(self.generate_barcode_individual)
        
        self.btn_generate_all = QPushButton("Generate Semua Barcode")
        self.btn_generate_all.clicked.connect(self.generate_semua_barcode)
        
        btn_layout.addWidget(self.btn_generate_single)
        btn_layout.addWidget(self.btn_generate_all)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)

        # Tabel produk (untuk pilih produk yang akan digenerate barcode-nya)
        self.table_produk = QTableWidget(0, 3)
        self.table_produk.setHorizontalHeaderLabels(["ID", "Barcode", "Nama"])
        layout.addWidget(QLabel("Pilih Produk:"))
        layout.addWidget(self.table_produk)

        # Muat data produk
        self.muat_produk()

    def muat_produk(self):
        """Muat semua produk ke tabel"""
        self.table_produk.setRowCount(0)
        produk_list = semua_produk()
        
        for row, (id_produk, barcode, nama, harga, stok) in enumerate(produk_list):
            self.table_produk.insertRow(row)
            self.table_produk.setItem(row, 0, QTableWidgetItem(str(id_produk)))
            self.table_produk.setItem(row, 1, QTableWidgetItem(barcode))
            self.table_produk.setItem(row, 2, QTableWidgetItem(nama))

    def generate_barcode_individual(self):
        """Generate barcode untuk satu produk"""
        barcode = self.input_barcode.text().strip()
        nama_produk = self.input_nama.text().strip()
        
        if not barcode or not nama_produk:
            QMessageBox.warning(self, "Input Tidak Lengkap", "Barcode dan nama produk harus diisi.")
            return
        
        try:
            # Generate barcode
            from pathlib import Path
            output_path = f"barcode/{barcode}_{nama_produk.replace(' ', '_')}.png"
            barcode_path = generate_barcode_gambar(barcode, nama_produk, output_path)
            
            QMessageBox.information(
                self, 
                "Berhasil", 
                f"Barcode berhasil dibuat:\n{barcode_path}"
            )
            
            # Refresh tabel
            self.muat_produk()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal generate barcode:\n{str(e)}")

    def generate_semua_barcode(self):
        """Generate barcode untuk semua produk"""
        reply = QMessageBox.question(
            self,
            "Konfirmasi",
            "Apakah Anda yakin ingin generate barcode untuk semua produk?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                hasil = generate_semua_barcode_gambar()
                QMessageBox.information(
                    self,
                    "Berhasil",
                    f"Berhasil generate {len(hasil)} barcode.\nLihat folder 'barcode' untuk hasilnya."
                )
                # Refresh tabel
                self.muat_produk()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal generate semua barcode:\n{str(e)}")