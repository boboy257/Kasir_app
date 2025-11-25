from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QHBoxLayout,
    QLineEdit, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QDialog, QRadioButton, QButtonGroup
)
from src.database import (
    tambah_produk, 
    semua_produk, 
    cari_produk_by_id, 
    update_produk, 
    hapus_produk,
    update_stok_produk 
)

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
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Barcode", "Nama", "Harga", "Stok", "Aksi"])
        layout.addWidget(self.table)

        self.muat_produk()
        self.atur_lebar_kolom()

    def atur_lebar_kolom(self):
        """Atur lebar kolom tabel agar lebih rapi"""
        # Kolom ID
        self.table.setColumnWidth(0, 50)   # ID
        # Kolom Barcode  
        self.table.setColumnWidth(1, 120)  # Barcode
        # Kolom Nama
        self.table.setColumnWidth(2, 200)  # Nama
        # Kolom Harga
        self.table.setColumnWidth(3, 100)  # Harga
        # Kolom Stok
        self.table.setColumnWidth(4, 80)   # Stok
        # Kolom Aksi
        self.table.setColumnWidth(5, 180)  # Aksi (Edit + Stok + Hapus)

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
        for row, (id_produk, barcode, nama, harga, stok) in enumerate(produk_list):
            self.table.insertRow(row)
        
            # Kolom ID
            self.table.setItem(row, 0, QTableWidgetItem(str(id_produk)))
             # Kolom Barcode
            self.table.setItem(row, 1, QTableWidgetItem(barcode))
            # Kolom Nama
            self.table.setItem(row, 2, QTableWidgetItem(nama))
            # Kolom Harga
            self.table.setItem(row, 3, QTableWidgetItem(f"Rp {harga}"))
            # Kolom Stok
            self.table.setItem(row, 4, QTableWidgetItem(str(stok)))
            
            # Kolom Aksi: Tombol Edit dan Hapus
            aksi_widget = QWidget()
            aksi_layout = QHBoxLayout(aksi_widget)
            aksi_layout.setContentsMargins(5, 2, 5, 2)
            aksi_layout.setSpacing(2)
            
            btn_edit = QPushButton("Edit")
            btn_edit.setFixedSize(50, 25)
            btn_edit.clicked.connect(lambda checked, id=id_produk: self.edit_produk(id))
            
            btn_stok = QPushButton("Stok")
            btn_edit.setFixedSize(50, 25)  
            btn_stok.clicked.connect(lambda checked, id=id_produk: self.manajemen_stok(id))

            btn_hapus = QPushButton("Hapus")
            btn_edit.setFixedSize(50, 25)
            btn_hapus.clicked.connect(lambda checked, id=id_produk: self.hapus_produk(id))
            
            aksi_layout.addWidget(btn_edit)
            aksi_layout.addWidget(btn_stok)
            aksi_layout.addWidget(btn_hapus)
            aksi_layout.addStretch()
            
            self.table.setCellWidget(row, 5, aksi_widget)

    def edit_produk(self, id_produk):
        """Fungsi untuk edit produk"""
        
        # Ambil data produk dari database
        produk = cari_produk_by_id(id_produk)
        if produk:
            id_produk, barcode, nama, harga, stok = produk
            
            # Isi form input dengan data produk
            self.barcode_input.setText(barcode)
            self.nama_input.setText(nama)
            self.harga_input.setText(str(harga))
            self.stok_input.setText(str(stok))
            
            # Ganti tombol simpan menjadi tombol update
            self.btn_simpan.setText("Update Produk")
            self.btn_simpan.clicked.disconnect()  # Hapus koneksi sebelumnya
            self.btn_simpan.clicked.connect(lambda: self.update_produk(id_produk))

    def update_produk(self, id_produk):
        """Fungsi untuk update produk"""

        barcode = self.barcode_input.text().strip()
        nama = self.nama_input.text().strip()
        harga = self.harga_input.text().strip()
        stok = self.stok_input.text().strip()

        if not barcode or not nama or not harga:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Input Tidak Lengkap", "Lengkapi semua data.")
            return

        try:
            harga = float(harga)
            stok = int(stok) if stok else 0
        except ValueError:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Input Salah", "Harga harus angka.")
            return

        update_produk(id_produk, barcode, nama, harga, stok)
        self.muat_produk()

        # Kembalikan tombol ke mode simpan
        self.btn_simpan.setText("Simpan Produk")
        self.btn_simpan.clicked.disconnect()
        self.btn_simpan.clicked.connect(self.simpan_produk)

        # Clear form
        self.barcode_input.clear()
        self.nama_input.clear()
        self.harga_input.clear()
        self.stok_input.clear()

    def hapus_produk(self, id_produk):
        """Fungsi untuk hapus produk"""

        reply = QMessageBox.question(
            self, 
            "Konfirmasi Hapus", 
            "Apakah Anda yakin ingin menghapus produk ini?", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            hapus_produk(id_produk)
            self.muat_produk() 

    def manajemen_stok(self, id_produk):
        """Fungsi untuk manajemen stok produk"""
        # Ambil data produk dari database
        produk = cari_produk_by_id(id_produk)
        if produk:
            id_produk, barcode, nama, harga, stok_awal = produk
            
            # Buat jendela dialog untuk input stok
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Manajemen Stok - {nama}")
            dialog.setGeometry(200, 200, 300, 150)
            
            layout = QVBoxLayout(dialog)
            
            # Label info stok saat ini
            label_info = QLabel(f"Stok saat ini: {stok_awal}")
            layout.addWidget(label_info)
            
            # Input jumlah stok
            input_layout = QHBoxLayout()
            input_layout.addWidget(QLabel("Jumlah:"))
            input_jumlah = QLineEdit()
            input_jumlah.setPlaceholderText("Masukkan jumlah stok")
            input_layout.addWidget(input_jumlah)
            layout.addLayout(input_layout)
            
            # Radio button untuk tambah/kurangi
            radio_layout = QHBoxLayout()
            
            radio_tambah = QRadioButton("Tambah Stok")
            radio_tambah.setChecked(True)  # Default pilih tambah
            radio_kurang = QRadioButton("Kurangi Stok")
            
            group_radio = QButtonGroup(dialog)
            group_radio.addButton(radio_tambah)
            group_radio.addButton(radio_kurang)
            
            radio_layout.addWidget(radio_tambah)
            radio_layout.addWidget(radio_kurang)
            layout.addLayout(radio_layout)
            
            # Tombol simpan
            btn_simpan = QPushButton("Simpan")
            btn_simpan.clicked.connect(lambda: self.simpan_manajemen_stok(
                id_produk, input_jumlah.text(), radio_tambah.isChecked(), stok_awal, dialog
            ))
            layout.addWidget(btn_simpan)
            
            dialog.exec()   

    def simpan_manajemen_stok(self, id_produk, jumlah_str, is_tambah, stok_awal, dialog):
            """Fungsi untuk menyimpan perubahan stok"""
            
            if not jumlah_str:
                QMessageBox.warning(self, "Input Tidak Lengkap", "Jumlah stok harus diisi.")
                return
            
            try:
                jumlah = int(jumlah_str)
                if jumlah <= 0:
                    QMessageBox.warning(self, "Input Salah", "Jumlah harus lebih dari 0.")
                    return
            except ValueError:
                QMessageBox.warning(self, "Input Salah", "Jumlah harus angka.")
                return
            
            # Hitung stok baru
            if is_tambah:
                stok_baru = stok_awal + jumlah
            else:
                if jumlah > stok_awal:
                    QMessageBox.warning(self, "Stok Tidak Cukup", f"Stok hanya {stok_awal}, tidak bisa dikurangi {jumlah}.")
                    return
                stok_baru = stok_awal - jumlah
            
            # Update stok di database
            update_stok_produk(id_produk, stok_baru)
            
            # Refresh tabel
            self.muat_produk()
            
            # Tutup dialog
            dialog.close()
            
            QMessageBox.information(self, "Berhasil", f"Stok berhasil diupdate menjadi {stok_baru}")