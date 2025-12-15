from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QHBoxLayout,
    QLineEdit, QLabel, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QFormLayout, QHeaderView, QAbstractItemView, QFrame
)
from PyQt6.QtCore import Qt, QEvent, QTimer
from PyQt6.QtGui import QPixmap, QImage
from src.database import semua_produk, generate_barcode_gambar, generate_semua_barcode_gambar, cari_produk_by_nama_partial
import os
import io

class GenerateBarcodeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generate Barcode Pro")
        self.setGeometry(100, 100, 1100, 650)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # --- 1. STYLE DARK MODE ---
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
            QLineEdit:focus { border: 2px solid #2196F3; background-color: #263238; }
            
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
            
            /* Area Preview */
            QLabel#PreviewArea {
                background-color: #ffffff; 
                border: 2px dashed #444;
                border-radius: 10px;
                color: #333;
            }

            /* Tombol Default */
            QPushButton { 
                background-color: #1E1E1E; border: 1px solid #555; 
                padding: 10px 20px; border-radius: 5px; font-weight: bold;
                min-height: 25px;
            }
            QPushButton:hover { background-color: #333; }
            
            QLabel { font-weight: bold; color: #bbb; background: transparent; }
        """)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- BAGIAN KIRI: KERJA & PREVIEW ---
        left_container = QFrame()
        left_container.setFixedWidth(400)
        left_container.setStyleSheet("background-color: #181818; border-radius: 10px; border: 1px solid #333;")
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_judul = QLabel("🛠️ Buat Barcode")
        lbl_judul.setStyleSheet("font-size: 18px; color: #2196F3; margin-bottom: 10px; border: none;")
        left_layout.addWidget(lbl_judul)

        # Form Input
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        
        self.input_barcode = QLineEdit()
        self.input_barcode.setPlaceholderText("Isi kode barcode...")
        self.input_barcode.textChanged.connect(self.live_preview_timer)
        self.input_barcode.installEventFilter(self)
        
        self.input_nama = QLineEdit()
        self.input_nama.setPlaceholderText("Nama produk...")
        self.input_nama.textChanged.connect(self.live_preview_timer)
        self.input_nama.installEventFilter(self)
        
        lbl_style = "font-weight: bold; color: #bbb; border: none;"
        form_layout.addRow(QLabel("Kode:", styleSheet=lbl_style), self.input_barcode)
        form_layout.addRow(QLabel("Nama:", styleSheet=lbl_style), self.input_nama)
        
        left_layout.addLayout(form_layout)
        
        # Area Preview
        left_layout.addSpacing(20)
        left_layout.addWidget(QLabel("Preview:", styleSheet=lbl_style))
        
        self.lbl_preview = QLabel("Masukkan Data untuk Preview")
        self.lbl_preview.setObjectName("PreviewArea")
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_preview.setMinimumHeight(150)
        left_layout.addWidget(self.lbl_preview)
        
        left_layout.addSpacing(20)

        # Tombol Aksi
        self.btn_simpan = QPushButton("Simpan Gambar")
        self.btn_simpan.setCursor(Qt.CursorShape.PointingHandCursor)
        # [STYLE HIJAU JELAS]
        self.btn_simpan.setStyleSheet("""
            QPushButton { background-color: #4CAF50; color: white; border: none; } 
            QPushButton:focus { border: 3px solid #FFF; }
        """)
        self.btn_simpan.clicked.connect(self.simpan_barcode)
        self.btn_simpan.installEventFilter(self)
        
        self.btn_generate_all = QPushButton("Generate Semua Stok")
        self.btn_generate_all.setCursor(Qt.CursorShape.PointingHandCursor)
        # [STYLE ORANGE JELAS]
        self.btn_generate_all.setStyleSheet("""
            QPushButton { background-color: #FF9800; color: white; border: none; }
            QPushButton:focus { border: 3px solid #FFF; }
        """)
        self.btn_generate_all.clicked.connect(self.generate_semua_barcode)
        self.btn_generate_all.installEventFilter(self)

        left_layout.addWidget(self.btn_simpan)
        left_layout.addWidget(self.btn_generate_all)
        left_layout.addStretch()
        
        main_layout.addWidget(left_container)

        # --- BAGIAN KANAN: TABEL DATA ---
        right_container = QVBoxLayout()
        
        # Search Bar
        search_layout = QHBoxLayout()
        lbl_cari = QLabel("🔍 Cari Produk:")
        lbl_cari.setStyleSheet("border: none;")
        
        self.input_cari = QLineEdit()
        self.input_cari.setPlaceholderText("Ketik nama produk...")
        self.input_cari.textChanged.connect(self.cari_produk)
        self.input_cari.installEventFilter(self)
        
        search_layout.addWidget(lbl_cari)
        search_layout.addWidget(self.input_cari)
        right_container.addLayout(search_layout)

        # Tabel
        self.table_produk = QTableWidget(0, 3)
        self.table_produk.setHorizontalHeaderLabels(["ID", "Barcode", "Nama"])
        self.table_produk.setColumnHidden(0, True)
        self.table_produk.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_produk.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_produk.setAlternatingRowColors(True)
        self.table_produk.setStyleSheet("QTableWidget { alternate-background-color: #252525; }")
        
        self.table_produk.itemClicked.connect(self.isi_form)
        self.table_produk.installEventFilter(self)
        
        header = self.table_produk.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        right_container.addWidget(self.table_produk)
        
        right_container.addWidget(QLabel("Navigasi: Kanan/Kiri (Pindah Kolom) | Enter | Ctrl+Bawah (Tabel)", styleSheet="color: #777; font-size: 11px; font-style: italic; border: none;"))
        
        main_layout.addLayout(right_container)

        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.update_preview)

        self.muat_produk()
        self.installEventFilter(self)
        self.input_barcode.setFocus() # Fokus awal

    # --- LOGIKA NAVIGASI KEYBOARD ---
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            
            # GLOBAL
            if event.key() == Qt.Key.Key_Escape: self.close(); return True
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Down:
                if self.table_produk.rowCount() > 0: self.table_produk.setFocus(); self.table_produk.selectRow(0); return True

            # 1. INPUT BARCODE
            if obj == self.input_barcode:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Down): self.input_nama.setFocus(); return True
                # [BARU] Kanan -> Loncat ke Cari
                if event.key() == Qt.Key.Key_Right: self.input_cari.setFocus(); return True 
            
            # 2. INPUT NAMA
            elif obj == self.input_nama:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Down): self.btn_simpan.setFocus(); return True
                if event.key() == Qt.Key.Key_Up: self.input_barcode.setFocus(); return True
                # [BARU] Kanan -> Loncat ke Cari
                if event.key() == Qt.Key.Key_Right: self.input_cari.setFocus(); return True

            # 3. TOMBOL SIMPAN (HIJAU)
            elif obj == self.btn_simpan:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.btn_simpan.click(); return True
                if event.key() == Qt.Key.Key_Down: self.btn_generate_all.setFocus(); return True
                if event.key() == Qt.Key.Key_Up: self.input_nama.setFocus(); return True
                # [BARU] Kanan -> Loncat ke Tabel (karena sejajar)
                if event.key() == Qt.Key.Key_Right: 
                    if self.table_produk.rowCount() > 0: self.table_produk.setFocus(); self.table_produk.selectRow(0); return True

            # 4. TOMBOL GENERATE ALL (ORANGE)
            elif obj == self.btn_generate_all:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.btn_generate_all.click(); return True
                if event.key() == Qt.Key.Key_Up: self.btn_simpan.setFocus(); return True
                # [BARU] Kanan -> Loncat ke Tabel
                if event.key() == Qt.Key.Key_Right: 
                     if self.table_produk.rowCount() > 0: self.table_produk.setFocus(); self.table_produk.selectRow(0); return True

            # 5. INPUT CARI
            elif obj == self.input_cari:
                if event.key() == Qt.Key.Key_Down: 
                    if self.table_produk.rowCount() > 0: self.table_produk.setFocus(); self.table_produk.selectRow(0); return True
                # [BARU] Kiri -> Balik ke Barcode
                if event.key() == Qt.Key.Key_Left: self.input_barcode.setFocus(); return True

            # 6. TABEL
            elif obj == self.table_produk:
                if event.key() == Qt.Key.Key_Up and self.table_produk.currentRow() <= 0: self.input_cari.setFocus(); return True
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.isi_form(); return True
                # [BARU] Kiri -> Balik ke Tombol Simpan
                if event.key() == Qt.Key.Key_Left: self.btn_simpan.setFocus(); return True

        return super().eventFilter(obj, event)

    def live_preview_timer(self):
        self.preview_timer.start(300)

    def update_preview(self):
        barcode_val = self.input_barcode.text().strip()
        nama_val = self.input_nama.text().strip()
        
        if not barcode_val or not nama_val:
            self.lbl_preview.setText("Data belum lengkap...")
            self.lbl_preview.setPixmap(QPixmap()) 
            return

        try:
            from barcode import Code128
            from barcode.writer import ImageWriter
            from PIL import Image, ImageDraw, ImageFont, ImageQt
            
            code = Code128(barcode_val, writer=ImageWriter())
            buffer = io.BytesIO()
            code.write(buffer)
            buffer.seek(0)
            img = Image.open(buffer)
            
            new_height = img.height + 40
            new_img = Image.new('RGB', (img.width, new_height), 'white')
            new_img.paste(img, (0, 0))
            draw = ImageDraw.Draw(new_img)
            
            try: font = ImageFont.load_default()
            except: pass
            
            bbox = draw.textbbox((0, 0), nama_val)
            text_width = bbox[2] - bbox[0]
            x = (img.width - text_width) // 2
            y = img.height + 5
            draw.text((x, y), nama_val, fill='black')
            
            qt_img = ImageQt.ImageQt(new_img)
            pixmap = QPixmap.fromImage(qt_img)
            self.lbl_preview.setPixmap(pixmap.scaled(300, 150, Qt.AspectRatioMode.KeepAspectRatio))
            
        except Exception as e:
            self.lbl_preview.setText(f"Gagal Preview: {e}")

    def isi_form(self):
        row = self.table_produk.currentRow()
        if row >= 0:
            barcode = self.table_produk.item(row, 1).text()
            nama = self.table_produk.item(row, 2).text()
            self.input_barcode.setText(barcode)
            self.input_nama.setText(nama)
            self.btn_simpan.setFocus()

    def cari_produk(self):
        keyword = self.input_cari.text().strip()
        if not keyword: self.muat_produk(); return
        hasil = cari_produk_by_nama_partial(keyword)
        self.tampilkan_tabel(hasil)

    def muat_produk(self):
        data = semua_produk()
        self.tampilkan_tabel(data)

    def tampilkan_tabel(self, data):
        self.table_produk.setRowCount(0)
        for row, (id_prod, barcode, nama, harga, stok) in enumerate(data):
            self.table_produk.insertRow(row)
            self.table_produk.setItem(row, 0, QTableWidgetItem(str(id_prod)))
            self.table_produk.setItem(row, 1, QTableWidgetItem(barcode))
            self.table_produk.setItem(row, 2, QTableWidgetItem(nama))

    def simpan_barcode(self):
        barcode = self.input_barcode.text().strip()
        nama = self.input_nama.text().strip()
        if not barcode or not nama:
            QMessageBox.warning(self, "Input", "Isi Barcode dan Nama dulu.")
            return
        
        try:
            folder = "barcode"
            if not os.path.exists(folder): os.makedirs(folder)
            path = f"{folder}/{barcode}_{nama.replace(' ', '_')}.png"
            generate_barcode_gambar(barcode, nama, path)
            QMessageBox.information(self, "Berhasil", f"Disimpan di:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def generate_semua_barcode(self):
        reply = QMessageBox.question(self, "Konfirmasi", "Generate semua stok?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                hasil = generate_semua_barcode_gambar()
                QMessageBox.information(self, "Selesai", f"{len(hasil)} barcode dibuat.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def set_current_user(self, username):
        self.current_user = username