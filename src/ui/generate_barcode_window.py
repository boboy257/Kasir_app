from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QHBoxLayout,
    QLineEdit, QLabel, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QFormLayout, QHeaderView, QAbstractItemView, QFrame
)
from PyQt6.QtCore import Qt, QEvent 
from src.database import semua_produk, generate_barcode_gambar, generate_semua_barcode_gambar

class GenerateBarcodeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generate Barcode")
        self.setGeometry(100, 100, 900, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # --- STYLE DARK MODE ---
        central_widget.setStyleSheet("""
            QWidget { 
                background-color: #121212; 
                color: #e0e0e0; 
                font-family: 'Segoe UI'; 
                font-size: 13px; 
                outline: none; 
            }
            QLineEdit { 
                background-color: #1E1E1E; 
                border: 1px solid #333; 
                padding: 8px; 
                color: white; 
                border-radius: 4px; 
            }
            QLineEdit:focus { border: 2px solid #2196F3; }
            
            QTableWidget { 
                background-color: #1E1E1E; 
                gridline-color: #333; 
                border: 1px solid #333; 
            }
            QTableWidget::item:selected { background-color: #2196F3; color: white; }
            QTableWidget:focus { border: 2px solid #2196F3; }

            QHeaderView::section { 
                background-color: #252525; 
                color: white; 
                padding: 8px; 
                border: none; 
                font-weight: bold; 
            }
            
            QPushButton { 
                background-color: #1E1E1E; 
                border: 1px solid #555; 
                padding: 8px; 
                border-radius: 4px; 
                font-weight: bold; 
            }
            QPushButton:hover { background-color: #333; }
            QPushButton:focus { border: 2px solid #ffffff; }
            
            QLabel { font-weight: bold; color: #bbb; background: transparent; }
        """)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)

        # Form Container
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: #181818; border-radius: 8px; border: 1px solid #333;")
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(15, 15, 15, 15)
        
        self.input_barcode = QLineEdit()
        self.input_barcode.setPlaceholderText("Barcode")
        self.input_barcode.installEventFilter(self)
        
        self.input_nama = QLineEdit()
        self.input_nama.setPlaceholderText("Nama Produk")
        self.input_nama.installEventFilter(self)
        
        form_layout.addRow("Barcode:", self.input_barcode)
        form_layout.addRow("Nama Produk:", self.input_nama)
        
        layout.addWidget(form_frame)

        # Tombol
        btn_layout = QHBoxLayout()
        self.btn_generate_single = QPushButton("Generate Barcode Individual")
        self.btn_generate_single.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_generate_single.setStyleSheet("color: #2196F3; border: 1px solid #2196F3;")
        self.btn_generate_single.clicked.connect(self.generate_barcode_individual)
        self.btn_generate_single.installEventFilter(self)
        
        self.btn_generate_all = QPushButton("Generate Semua Barcode")
        self.btn_generate_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_generate_all.setStyleSheet("color: #4CAF50; border: 1px solid #4CAF50;")
        self.btn_generate_all.clicked.connect(self.generate_semua_barcode)
        self.btn_generate_all.installEventFilter(self)
        
        btn_layout.addWidget(self.btn_generate_single)
        btn_layout.addWidget(self.btn_generate_all)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)

        # Tabel
        self.table_produk = QTableWidget(0, 3)
        self.table_produk.setHorizontalHeaderLabels(["ID", "Barcode", "Nama"])
        self.table_produk.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_produk.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_produk.setAlternatingRowColors(True)
        self.table_produk.setStyleSheet("QTableWidget { alternate-background-color: #252525; }")
        
        # Klik tabel -> isi form
        self.table_produk.itemClicked.connect(self.isi_form)
        self.table_produk.installEventFilter(self)
        
        header = self.table_produk.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(QLabel("Pilih Produk dari Tabel:"))
        layout.addWidget(self.table_produk)

        self.muat_produk()
        
        # [PENTING] Pasang telinga ESC
        self.installEventFilter(self)

    # [LOGIKA ESC]
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape:
                self.close()
                return True
        return super().eventFilter(obj, event)

    def isi_form(self):
        row = self.table_produk.currentRow()
        if row >= 0:
            barcode = self.table_produk.item(row, 1).text()
            nama = self.table_produk.item(row, 2).text()
            self.input_barcode.setText(barcode)
            self.input_nama.setText(nama)

    def muat_produk(self):
        self.table_produk.setRowCount(0)
        produk_list = semua_produk()
        for row, (id_produk, barcode, nama, harga, stok) in enumerate(produk_list):
            self.table_produk.insertRow(row)
            self.table_produk.setItem(row, 0, QTableWidgetItem(str(id_produk)))
            self.table_produk.setItem(row, 1, QTableWidgetItem(barcode))
            self.table_produk.setItem(row, 2, QTableWidgetItem(nama))

    def generate_barcode_individual(self):
        barcode = self.input_barcode.text().strip()
        nama_produk = self.input_nama.text().strip()
        if not barcode or not nama_produk:
            QMessageBox.warning(self, "Input Tidak Lengkap", "Barcode dan nama produk harus diisi.")
            return
        try:
            # Gunakan path absolut/relatif yang aman
            import os
            barcode_folder = "barcode"
            if not os.path.exists(barcode_folder):
                os.makedirs(barcode_folder)
                
            filename = f"{barcode_folder}/{barcode}_{nama_produk.replace(' ', '_')}.png"
            barcode_path = generate_barcode_gambar(barcode, nama_produk, filename)
            QMessageBox.information(self, "Berhasil", f"Barcode dibuat:\n{barcode_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal generate: {str(e)}")

    def generate_semua_barcode(self):
        reply = QMessageBox.question(self, "Konfirmasi", "Generate semua barcode? (Bisa memakan waktu)", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                hasil = generate_semua_barcode_gambar()
                QMessageBox.information(self, "Berhasil", f"Berhasil generate {len(hasil)} barcode.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal: {str(e)}")

    def set_current_user(self, username):
        self.current_user = username