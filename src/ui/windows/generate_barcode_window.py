"""
Generate Barcode Window - REFACTORED VERSION
=============================================
Menggunakan BaseWindow untuk konsistensi
"""

from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QHBoxLayout,
    QLineEdit, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QFormLayout, QHeaderView, QAbstractItemView, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
import io

from src.ui.base.base_window import BaseWindow
from src.ui.base.style_manager import StyleManager
from src.database import (
    semua_produk, generate_barcode_gambar, 
    generate_semua_barcode_gambar, cari_produk_by_nama_partial
)

class GenerateBarcodeWindow(BaseWindow):
    """
    Window generate barcode
    
    Features:
    - Live preview barcode
    - Generate single barcode
    - Generate all barcodes
    - Search products
    """
    
    def __init__(self):
        super().__init__()
        
        self.setup_ui()
        self.setup_navigation()
        self.muat_produk()
        
        # Preview timer
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.update_preview)
        
        # Window properties
        self.setWindowTitle("Generate Barcode Pro")
        self.setGeometry(100, 100, 1100, 650)
    
    def setup_ui(self):
        """Setup UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # --- KIRI: Form & Preview ---
        left_container = QFrame()
        left_container.setFixedWidth(400)
        left_container.setStyleSheet("""
            QFrame {
                background-color: #181818; 
                border-radius: 10px; 
                border: 1px solid #333;
            }
        """)
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
        
        # Preview Area
        left_layout.addSpacing(20)
        left_layout.addWidget(QLabel("Preview:", styleSheet=lbl_style))
        
        self.lbl_preview = QLabel("Masukkan Data untuk Preview")
        self.lbl_preview.setObjectName("PreviewArea")
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_preview.setMinimumHeight(150)
        self.lbl_preview.setStyleSheet("""
            QLabel#PreviewArea {
                background-color: #ffffff; 
                border: 2px dashed #444;
                border-radius: 10px;
                color: #333;
            }
        """)
        left_layout.addWidget(self.lbl_preview)
        
        left_layout.addSpacing(20)
        
        # Tombol Aksi
        style = StyleManager()
        
        self.btn_simpan = QPushButton("Simpan Gambar")
        self.btn_simpan.setStyleSheet(style.get_button_style('success'))
        self.btn_simpan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_simpan.clicked.connect(self.simpan_barcode)
        self.btn_simpan.installEventFilter(self)
        
        self.btn_generate_all = QPushButton("Generate Semua Stok")
        self.btn_generate_all.setStyleSheet(style.get_button_style('warning'))
        self.btn_generate_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_generate_all.clicked.connect(self.generate_semua_barcode)
        self.btn_generate_all.installEventFilter(self)
        
        left_layout.addWidget(self.btn_simpan)
        left_layout.addWidget(self.btn_generate_all)
        left_layout.addStretch()
        
        main_layout.addWidget(left_container)
        
        # --- KANAN: Table ---
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
        
        # Table
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
        
        # Info
        right_container.addWidget(QLabel(
            "Navigasi: Kanan/Kiri (Pindah Kolom) | Enter | Ctrl+Bawah (Tabel)",
            styleSheet="color: #777; font-size: 11px; font-style: italic; border: none;"
        ))
        
        main_layout.addLayout(right_container)
        
        # Initial focus
        self.input_barcode.setFocus()
    
    def setup_navigation(self):
        """Setup keyboard navigation"""
        # Barcode: Enter/Down = Nama, Right = Cari
        self.register_navigation(self.input_barcode, {
            Qt.Key.Key_Return: self.input_nama,
            Qt.Key.Key_Down: self.input_nama,
            Qt.Key.Key_Right: self.input_cari
        })
        
        # Nama: Enter/Down = Simpan, Up = Barcode, Right = Cari
        self.register_navigation(self.input_nama, {
            Qt.Key.Key_Return: self.btn_simpan,
            Qt.Key.Key_Down: self.btn_simpan,
            Qt.Key.Key_Up: self.input_barcode,
            Qt.Key.Key_Right: self.input_cari
        })
        
        # Btn Simpan
        self.register_navigation(self.btn_simpan, {
            Qt.Key.Key_Return: self.simpan_barcode,
            Qt.Key.Key_Down: self.btn_generate_all,
            Qt.Key.Key_Up: self.input_nama,
            Qt.Key.Key_Right: lambda: self.focus_table_first_row(self.table_produk)
        })
        
        # Btn Generate All
        self.register_navigation(self.btn_generate_all, {
            Qt.Key.Key_Return: self.generate_semua_barcode,
            Qt.Key.Key_Up: self.btn_simpan,
            Qt.Key.Key_Right: lambda: self.focus_table_first_row(self.table_produk)
        })
        
        # Input Cari
        self.register_navigation(self.input_cari, {
            Qt.Key.Key_Down: lambda: self.focus_table_first_row(self.table_produk),
            Qt.Key.Key_Left: self.input_barcode
        })
        
        # Table: Enter = isi form
        self.register_navigation(self.table_produk, {
            Qt.Key.Key_Return: self.isi_form
        })
    
    def eventFilter(self, obj, event):
        """Handle special keyboard events"""
        from PyQt6.QtCore import QEvent
        
        if event.type() == QEvent.Type.KeyPress:
            # Ctrl+Down = Pindah ke table
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Down:
                self.focus_table_first_row(self.table_produk)
                return True
            
            # Table: Up di baris 0 = balik ke cari, Left = balik ke simpan
            if obj == self.table_produk:
                if event.key() == Qt.Key.Key_Up and self.table_produk.currentRow() <= 0:
                    self.input_cari.setFocus()
                    return True
                elif event.key() == Qt.Key.Key_Left:
                    self.btn_simpan.setFocus()
                    return True
        
        return super().eventFilter(obj, event)
    
    def live_preview_timer(self):
        """Trigger preview after typing pause"""
        self.preview_timer.start(300)
    
    def update_preview(self):
        """Update preview barcode"""
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
            
            try:
                font = ImageFont.load_default()
            except:
                pass
            
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
        """Fill form from selected table row"""
        row = self.table_produk.currentRow()
        if row >= 0:
            barcode = self.table_produk.item(row, 1).text()
            nama = self.table_produk.item(row, 2).text()
            self.input_barcode.setText(barcode)
            self.input_nama.setText(nama)
            self.btn_simpan.setFocus()
    
    def cari_produk(self):
        """Search products"""
        keyword = self.input_cari.text().strip()
        if not keyword:
            self.muat_produk()
            return
        
        hasil = cari_produk_by_nama_partial(keyword)
        self.tampilkan_tabel(hasil)
    
    def muat_produk(self):
        """Load all products"""
        data = semua_produk()
        self.tampilkan_tabel(data)
    
    def tampilkan_tabel(self, data):
        """Display data in table"""
        self.table_produk.setRowCount(0)
        for row, (id_prod, barcode, nama, harga, stok) in enumerate(data):
            self.table_produk.insertRow(row)
            self.table_produk.setItem(row, 0, QTableWidgetItem(str(id_prod)))
            self.table_produk.setItem(row, 1, QTableWidgetItem(barcode))
            self.table_produk.setItem(row, 2, QTableWidgetItem(nama))
    
    def simpan_barcode(self):
        """Save barcode image"""
        barcode = self.input_barcode.text().strip()
        nama = self.input_nama.text().strip()
        
        if not barcode or not nama:
            self.show_warning("Input", "Isi Barcode dan Nama dulu.")
            return
        
        try:
            import os
            folder = "barcode"
            if not os.path.exists(folder):
                os.makedirs(folder)
            
            path = f"{folder}/{barcode}_{nama.replace(' ', '_')}.png"
            generate_barcode_gambar(barcode, nama, path)
            self.show_success("Berhasil", f"Disimpan di:\n{path}")
        except Exception as e:
            self.show_error("Error", str(e))
    
    def generate_semua_barcode(self):
        """Generate all barcodes"""
        if self.confirm_action("Konfirmasi", "Generate semua stok?"):
            try:
                hasil = generate_semua_barcode_gambar()
                self.show_success("Selesai", f"{len(hasil)} barcode dibuat.")
            except Exception as e:
                self.show_error("Error", str(e))