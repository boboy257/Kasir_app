from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QHBoxLayout,
    QLineEdit, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QAbstractItemView, QFormLayout, QFrame
)
from PyQt6.QtCore import Qt, QEvent 
from PyQt6.QtGui import QIntValidator, QDoubleValidator
from src.database import (
    tambah_produk_dengan_log, semua_produk, cari_produk_by_id, 
    update_produk_dengan_log, hapus_produk_dengan_log,
    cari_produk_by_nama_partial
)

class ProdukWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manajemen Produk")
        self.setGeometry(100, 100, 1000, 650)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # --- STYLE DARK MODE ---
        self.setStyleSheet("""
            QWidget { 
                background-color: #121212; 
                color: #e0e0e0; 
                font-family: 'Segoe UI', sans-serif; 
                font-size: 13px;
                outline: none;
            }
            
            QLineEdit { 
                background-color: #1E1E1E; border: 1px solid #333; 
                padding: 10px; color: white; border-radius: 5px;
            }
            QLineEdit:focus { border: 2px solid #00E5FF; background-color: #263238; }
            
            QTableWidget { 
                background-color: #1E1E1E; gridline-color: #333; 
                border: 1px solid #333; border-radius: 5px;
            }
            QTableWidget:focus { border: 2px solid #00E5FF; }
            QTableWidget::item:selected { background-color: #00E5FF; color: #000000; }
            
            QHeaderView::section { 
                background-color: #252525; color: white; 
                padding: 8px; border: none; font-weight: bold; 
            }
            
            QLabel { font-weight: bold; color: #bbb; background: transparent; }
        """)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # --- FORM CONTAINER ---
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: #181818; border-radius: 10px; border: 1px solid #333;")
        form_layout_main = QVBoxLayout(form_frame)
        form_layout_main.setContentsMargins(20, 20, 20, 20)
        
        lbl_judul = QLabel("📦 Input / Edit Produk")
        lbl_judul.setStyleSheet("font-size: 16px; color: #00E5FF; margin-bottom: 10px;")
        form_layout_main.addWidget(lbl_judul)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(20)
        
        # Kiri
        left_form = QFormLayout()
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Scan/Ketik Barcode")
        self.barcode_input.installEventFilter(self)

        self.nama_input = QLineEdit()
        self.nama_input.setPlaceholderText("Nama Produk")
        self.nama_input.installEventFilter(self)

        left_form.addRow("Barcode:", self.barcode_input)
        left_form.addRow("Nama:", self.nama_input)
        
        # Kanan
        right_form = QFormLayout()
        self.harga_input = QLineEdit()
        self.harga_input.setPlaceholderText("Rp 0")
        self.harga_input.setValidator(QDoubleValidator(0.0, 999999999.0, 2))
        self.harga_input.installEventFilter(self)

        self.stok_input = QLineEdit()
        self.stok_input.setPlaceholderText("0")
        self.stok_input.setValidator(QIntValidator(0, 100000))
        self.stok_input.installEventFilter(self)

        right_form.addRow("Harga (Rp):", self.harga_input)
        right_form.addRow("Stok Awal:", self.stok_input)
        
        input_layout.addLayout(left_form)
        input_layout.addLayout(right_form)
        form_layout_main.addLayout(input_layout)

        # Tombol Aksi
        btn_layout = QHBoxLayout()
        self.btn_simpan = QPushButton("Simpan Produk")
        self.btn_simpan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_simpan.clicked.connect(self.simpan_produk)
        self.btn_simpan.installEventFilter(self)
        
        # [STYLE TOMBOL SIMPAN AWAL]
        self.btn_simpan.setStyleSheet("""
            QPushButton { 
                background-color: #4CAF50; color: white; border: none; 
                padding: 12px; border-radius: 5px; font-weight: bold; 
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:focus { 
                border: 3px solid #ffffff; /* Border Putih Tebal */
                background-color: #43A047; 
            }
        """)
        
        self.btn_batal = QPushButton("Reset Form")
        self.btn_batal.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_batal.clicked.connect(self.reset_form)
        self.btn_batal.installEventFilter(self)
        
        # [STYLE TOMBOL RESET]
        self.btn_batal.setStyleSheet("""
            QPushButton { 
                background-color: #424242; color: white; border: none; 
                padding: 12px; border-radius: 5px; 
            }
            QPushButton:hover { background-color: #616161; }
            QPushButton:focus { 
                border: 3px solid #ffffff; /* Border Putih Tebal */
                background-color: #757575;
            }
        """)
        
        btn_layout.addWidget(self.btn_simpan)
        btn_layout.addWidget(self.btn_batal)
        form_layout_main.addLayout(btn_layout)
        
        layout.addWidget(form_frame)

        # --- PENCARIAN & TABEL ---
        search_layout = QHBoxLayout()
        lbl_cari = QLabel("🔍 Cari Produk:")
        self.input_cari = QLineEdit()
        self.input_cari.setPlaceholderText("Ketik nama produk...")
        self.input_cari.textChanged.connect(self.cari_produk)
        self.input_cari.installEventFilter(self)
        
        search_layout.addWidget(lbl_cari)
        search_layout.addWidget(self.input_cari)
        search_layout.addWidget(QLabel("Tips: Enter=Edit, Del=Hapus, Ctrl+Bawah=Tabel"))
        
        layout.addLayout(search_layout)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Barcode", "Nama", "Harga", "Stok"])
        self.table.setColumnHidden(0, True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget { alternate-background-color: #252525; }")
        self.table.itemClicked.connect(self.isi_form_dari_tabel)
        self.table.installEventFilter(self)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.table)

        self.id_produk_diedit = None
        self.muat_produk()
        self.installEventFilter(self) # ESC Global

    # --- NAVIGASI KEYBOARD ---
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape: self.close(); return True
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Down:
                if self.table.rowCount() > 0: self.table.setFocus(); self.table.selectRow(0); return True
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Up:
                self.barcode_input.setFocus(); return True

            # 1. BARCODE
            if obj == self.barcode_input:
                if event.key() == Qt.Key.Key_Right: self.harga_input.setFocus(); return True 
                if event.key() == Qt.Key.Key_Down: self.nama_input.setFocus(); return True 
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.nama_input.setFocus(); return True

            # 2. HARGA
            elif obj == self.harga_input:
                if event.key() == Qt.Key.Key_Left: self.barcode_input.setFocus(); return True 
                if event.key() == Qt.Key.Key_Down: self.stok_input.setFocus(); return True 
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.stok_input.setFocus(); self.stok_input.selectAll(); return True

            # 3. NAMA
            elif obj == self.nama_input:
                if event.key() == Qt.Key.Key_Up: self.barcode_input.setFocus(); return True 
                if event.key() == Qt.Key.Key_Right: self.stok_input.setFocus(); return True 
                if event.key() == Qt.Key.Key_Down: self.btn_simpan.setFocus(); return True 
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.harga_input.setFocus(); self.harga_input.selectAll(); return True

            # 4. STOK
            elif obj == self.stok_input:
                if event.key() == Qt.Key.Key_Up: self.harga_input.setFocus(); return True 
                if event.key() == Qt.Key.Key_Left: self.nama_input.setFocus(); return True 
                if event.key() == Qt.Key.Key_Down: self.btn_batal.setFocus(); return True 
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.btn_simpan.setFocus(); return True

            # 5. TOMBOL SIMPAN
            elif obj == self.btn_simpan:
                if event.key() == Qt.Key.Key_Up: self.nama_input.setFocus(); return True 
                if event.key() == Qt.Key.Key_Right: self.btn_batal.setFocus(); return True 
                if event.key() == Qt.Key.Key_Down: self.input_cari.setFocus(); return True 
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.btn_simpan.click(); return True

            # 6. TOMBOL RESET
            elif obj == self.btn_batal:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.btn_batal.click(); return True
                if event.key() == Qt.Key.Key_Left: self.btn_simpan.setFocus(); return True
                if event.key() == Qt.Key.Key_Up: self.stok_input.setFocus(); return True
                if event.key() == Qt.Key.Key_Down: self.input_cari.setFocus(); return True

            # 7. INPUT CARI
            elif obj == self.input_cari:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Down):
                    if self.table.rowCount() > 0: self.table.setFocus(); self.table.selectRow(0); return True
                elif event.key() == Qt.Key.Key_Up: self.btn_simpan.setFocus(); return True

            # 8. TABEL
            elif obj == self.table:
                if event.key() == Qt.Key.Key_Up and self.table.currentRow() <= 0: self.input_cari.setFocus(); return True
                if event.key() == Qt.Key.Key_F2 or event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.isi_form_dari_tabel(); return True
                if event.key() == Qt.Key.Key_Delete: self.hapus_produk(); return True

        return super().eventFilter(obj, event)

    def cari_produk(self):
        keyword = self.input_cari.text().strip()
        if not keyword: self.muat_produk(); return  
        hasil = cari_produk_by_nama_partial(keyword)
        self.tampilkan_data_di_tabel(hasil)

    def muat_produk(self):
        data = semua_produk()
        self.tampilkan_data_di_tabel(data)

    def tampilkan_data_di_tabel(self, data_list):
        self.table.setRowCount(0)
        for row, (id_produk, barcode, nama, harga, stok) in enumerate(data_list):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(id_produk)))
            self.table.setItem(row, 1, QTableWidgetItem(barcode))
            self.table.setItem(row, 2, QTableWidgetItem(nama))
            self.table.setItem(row, 3, QTableWidgetItem(f"Rp {int(harga):,}"))
            self.table.setItem(row, 4, QTableWidgetItem(str(stok)))

    def isi_form_dari_tabel(self):
        row = self.table.currentRow()
        if row >= 0:
            id_produk = self.table.item(row, 0).text()
            barcode = self.table.item(row, 1).text()
            nama = self.table.item(row, 2).text()
            harga_text = self.table.item(row, 3).text().replace("Rp ", "").replace(",", "").replace(".", "")
            stok = self.table.item(row, 4).text()

            self.barcode_input.setText(barcode)
            self.nama_input.setText(nama)
            self.harga_input.setText(harga_text)
            self.stok_input.setText(stok)

            self.id_produk_diedit = id_produk
            self.btn_simpan.setText("Update Produk")
            
            # [STYLE TOMBOL UPDATE - FOKUS JELAS]
            self.btn_simpan.setStyleSheet("""
                QPushButton { 
                    background-color: #FF9800; color: white; border: none; 
                    padding: 12px; border-radius: 5px; font-weight: bold; 
                }
                QPushButton:hover { background-color: #F57C00; }
                QPushButton:focus { 
                    border: 3px solid #ffffff; /* Border Putih Tebal */
                    background-color: #FFB74D;
                }
            """)
            self.barcode_input.setFocus()

    def reset_form(self):
        self.barcode_input.clear()
        self.nama_input.clear()
        self.harga_input.clear()
        self.stok_input.clear()
        self.input_cari.clear()
        
        self.id_produk_diedit = None
        self.btn_simpan.setText("Simpan Produk")
        
        # [STYLE TOMBOL SIMPAN - KEMBALI NORMAL]
        self.btn_simpan.setStyleSheet("""
            QPushButton { 
                background-color: #4CAF50; color: white; border: none; 
                padding: 12px; border-radius: 5px; font-weight: bold; 
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:focus { 
                border: 3px solid #ffffff; /* Border Putih Tebal */
                background-color: #43A047;
            }
        """)
        self.table.clearSelection()
        self.barcode_input.setFocus()

    def simpan_produk(self):
        barcode = self.barcode_input.text().strip()
        nama = self.nama_input.text().strip()
        harga_str = self.harga_input.text().strip().replace(".", "")
        stok_str = self.stok_input.text().strip()

        if not barcode or not nama or not harga_str:
            QMessageBox.warning(self, "Error", "Barcode, Nama, dan Harga wajib diisi.")
            return

        try:
            harga = float(harga_str)
            stok = int(stok_str) if stok_str else 0
        except ValueError:
            QMessageBox.warning(self, "Error", "Harga dan Stok harus angka.")
            return

        username = getattr(self, 'current_user', 'admin')

        if self.id_produk_diedit:
            update_produk_dengan_log(self.id_produk_diedit, barcode, nama, harga, stok, username)
            QMessageBox.information(self, "Berhasil", "Produk berhasil diupdate.")
        else:
            tambah_produk_dengan_log(barcode, nama, harga, stok, username)
            QMessageBox.information(self, "Berhasil", "Produk baru ditambahkan.")

        self.reset_form()
        self.muat_produk()

    def hapus_produk(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Pilih Produk", "Pilih produk di tabel dulu.")
            return

        nama = self.table.item(row, 2).text()
        id_produk = self.table.item(row, 0).text()

        reply = QMessageBox.question(
            self, "Konfirmasi Hapus", 
            f"Yakin ingin menghapus '{nama}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            username = getattr(self, 'current_user', 'admin')
            hapus_produk_dengan_log(id_produk, username)
            self.muat_produk()
            self.reset_form()

    def set_current_user(self, username):
        self.current_user = username