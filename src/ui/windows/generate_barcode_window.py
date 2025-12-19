"""
Generate Barcode Window - SmartNavigation REFACTORED
=====================================================
Complex layout: Form left + Table right dengan memory navigation
"""

from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QHBoxLayout,
    QLineEdit, QLabel, QPushButton, QFormLayout, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
import io

from src.ui.base.base_window import BaseWindow
from src.ui.base.style_manager import StyleManager
from src.ui.widgets.smart_table import SmartTable
from src.database import (
    semua_produk, generate_barcode_gambar, 
    generate_semua_barcode_gambar, cari_produk_by_nama_partial
)


class GenerateBarcodeWindow(BaseWindow):
    """Barcode generator dengan split layout navigation"""
    
    def __init__(self):
        super().__init__()
        
        self.setup_ui()
        self.setup_navigation()
        self.muat_produk()
        
        # Preview timer
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.update_preview)
        
        self.setWindowTitle("Generate Barcode Pro")
        self.setGeometry(100, 100, 1100, 650)
    
    def setup_ui(self):
        """Setup UI - Split layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # LEFT: Form & Preview
        left_container = QFrame()
        left_container.setFixedWidth(400)
        left_container.setStyleSheet(
            "QFrame { background-color: #181818; border-radius: 10px; border: 1px solid #333; }"
        )
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_judul = QLabel("🛠️ Buat Barcode")
        lbl_judul.setStyleSheet("font-size: 18px; color: #2196F3; margin-bottom: 10px; border: none;")
        left_layout.addWidget(lbl_judul)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        
        self.input_barcode = QLineEdit()
        self.input_barcode.setPlaceholderText("Isi kode barcode...")
        self.input_barcode.textChanged.connect(self.live_preview_timer)
        
        self.input_nama = QLineEdit()
        self.input_nama.setPlaceholderText("Nama produk...")
        self.input_nama.textChanged.connect(self.live_preview_timer)
        
        lbl_style = "font-weight: bold; color: #bbb; border: none;"
        form_layout.addRow(QLabel("Kode:", styleSheet=lbl_style), self.input_barcode)
        form_layout.addRow(QLabel("Nama:", styleSheet=lbl_style), self.input_nama)
        
        left_layout.addLayout(form_layout)
        
        # Preview
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
        
        # Action buttons
        style = StyleManager()
        
        self.btn_simpan = QPushButton("Simpan Gambar")
        self.btn_simpan.setStyleSheet(style.get_button_style('success'))
        self.btn_simpan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_simpan.clicked.connect(self.simpan_barcode)
        
        self.btn_generate_all = QPushButton("Generate Semua")
        self.btn_generate_all.setStyleSheet(style.get_button_style('warning'))
        self.btn_generate_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_generate_all.clicked.connect(self.generate_semua_barcode)
        
        left_layout.addWidget(self.btn_simpan)
        left_layout.addWidget(self.btn_generate_all)
        left_layout.addStretch()
        
        main_layout.addWidget(left_container)
        
        # RIGHT: Table
        right_container = QVBoxLayout()
        
        # Search
        search_layout = QHBoxLayout()
        lbl_cari = QLabel("🔍 Cari Produk:")
        lbl_cari.setStyleSheet("border: none;")
        
        self.input_cari = QLineEdit()
        self.input_cari.setPlaceholderText("Ketik nama produk... (Ctrl+F)")
        self.input_cari.textChanged.connect(self.cari_produk)
        
        search_layout.addWidget(lbl_cari)
        search_layout.addWidget(self.input_cari)
        right_container.addLayout(search_layout)
        
        # Table
        self.table_produk = SmartTable(0, 3)
        self.table_produk.setHorizontalHeaderLabels(["ID", "Barcode", "Nama"])
        self.table_produk.setColumnHidden(0, True)
        self.table_produk.stretch_column(2)
        self.table_produk.itemClicked.connect(self.isi_form)
        
        right_container.addWidget(self.table_produk)
        
        # Navigation info
        right_container.addWidget(QLabel(
            "F2/Enter=Load | ←→=Form↔Table | ESC=Close",
            styleSheet="color: #777; font-size: 11px; font-style: italic; border: none;"
        ))
        
        main_layout.addLayout(right_container)
        
        self.input_barcode.setFocus()
    
    def setup_navigation(self):
        """
        SmartNavigation untuk split layout:
        - Left side: Form vertical chain
        - Right side: Search + Table
        - Memory navigation: Form ↔ Table
        """
        
        # Left side: Vertical form chain
        self.register_navigation(self.input_barcode, {
            Qt.Key.Key_Return: self.input_nama,
            Qt.Key.Key_Down: self.input_nama,
            Qt.Key.Key_Right: self.input_cari  # Jump to right
        })
        
        self.register_navigation(self.input_nama, {
            Qt.Key.Key_Return: self.btn_simpan,
            Qt.Key.Key_Down: self.btn_simpan,
            Qt.Key.Key_Up: self.input_barcode,
            Qt.Key.Key_Right: self.input_cari
        })
        
        # Buttons (vertical)
        self.register_navigation(self.btn_simpan, {
            Qt.Key.Key_Return: self.simpan_barcode,
            Qt.Key.Key_Down: self.btn_generate_all,
            Qt.Key.Key_Up: self.input_nama,
            Qt.Key.Key_Right: lambda: self.focus_table_first_row(self.table_produk)
        })
        
        self.register_navigation(self.btn_generate_all, {
            Qt.Key.Key_Return: self.generate_semua_barcode,
            Qt.Key.Key_Up: self.btn_simpan,
            Qt.Key.Key_Right: lambda: self.focus_table_first_row(self.table_produk)
        })
        
        # Right side: Search
        self.register_navigation(self.input_cari, {
            Qt.Key.Key_Down: lambda: self.focus_table_first_row(self.table_produk),
            Qt.Key.Key_Left: self.input_barcode
        })
        
        # Table
        self.register_table_callbacks(self.table_produk, {
            'edit': self.isi_form,
            'focus_up': self.input_cari,
            'focus_down': self.btn_simpan
        })
        
        # Table: Left = Back to form
        self.register_navigation(self.table_produk, {
            Qt.Key.Key_Left: self.input_barcode
        })
    
    # Preview
    def live_preview_timer(self):
        """Trigger preview after typing pause"""
        self.preview_timer.start(300)
    
    def update_preview(self):
        """Live preview barcode"""
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
            
            # Add text below
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
            
            # Convert to QPixmap
            qt_img = ImageQt.ImageQt(new_img)
            pixmap = QPixmap.fromImage(qt_img)
            self.lbl_preview.setPixmap(pixmap.scaled(300, 150, Qt.AspectRatioMode.KeepAspectRatio))
            
        except Exception as e:
            self.lbl_preview.setText(f"Gagal Preview: {e}")
    
    # Form operations
    def isi_form(self):
        """Load data dari table ke form"""
        row = self.table_produk.currentRow()
        if row >= 0:
            barcode = self.table_produk.item(row, 1).text()
            nama = self.table_produk.item(row, 2).text()
            self.input_barcode.setText(barcode)
            self.input_nama.setText(nama)
            self.btn_simpan.setFocus()
    
    def cari_produk(self):
        """Real-time search"""
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
        """Display products"""
        self.table_produk.clear_table()
        
        from PyQt6.QtWidgets import QTableWidgetItem
        
        for row, (id_prod, barcode, nama, harga, stok) in enumerate(data):
            self.table_produk.insertRow(row)
            self.table_produk.setItem(row, 0, QTableWidgetItem(str(id_prod)))
            self.table_produk.setItem(row, 1, QTableWidgetItem(barcode))
            self.table_produk.setItem(row, 2, QTableWidgetItem(nama))
    
    def simpan_barcode(self):
        """Save single barcode"""
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