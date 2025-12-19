"""
Produk Window - SmartNavigation REFACTORED
===========================================
Form 2x2 grid + table dengan memory navigation
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QLabel, 
    QPushButton, QFormLayout, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator, QDoubleValidator

from src.ui.base.base_window import BaseWindow
from src.ui.base.style_manager import StyleManager
from src.ui.widgets.smart_table import SmartTable
from src.database import (
    tambah_produk_dengan_log, semua_produk, 
    update_produk_dengan_log, hapus_produk_dengan_log,
    cari_produk_by_nama_partial
)


class ProdukWindow(BaseWindow):
    """Product CRUD dengan smart 2D grid navigation"""
    
    def __init__(self):
        super().__init__()
        
        self.id_produk_diedit = None
        self.last_form_widget = None  # Memory navigation
        
        self.setup_ui()
        self.setup_navigation()
        
        self.setWindowTitle("Manajemen Produk")
        self.setGeometry(100, 100, 1000, 650)
        
        self.muat_produk()
    
    def setup_ui(self):
        """Setup UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Form container
        form_frame = QFrame()
        form_frame.setStyleSheet(
            "background-color: #181818; border-radius: 10px; border: 1px solid #333;"
        )
        form_layout_main = QVBoxLayout(form_frame)
        form_layout_main.setContentsMargins(20, 20, 20, 20)
        
        lbl_judul = QLabel("📦 Input / Edit Produk")
        lbl_judul.setStyleSheet("font-size: 16px; color: #00E5FF; margin-bottom: 10px;")
        form_layout_main.addWidget(lbl_judul)
        
        # 2x2 Grid input
        input_layout = QHBoxLayout()
        input_layout.setSpacing(20)
        
        # Left column
        left_form = QFormLayout()
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Scan/Ketik Barcode")
        
        self.nama_input = QLineEdit()
        self.nama_input.setPlaceholderText("Nama Produk")
        
        left_form.addRow("Barcode:", self.barcode_input)
        left_form.addRow("Nama:", self.nama_input)
        
        # Right column
        right_form = QFormLayout()
        
        self.harga_input = QLineEdit()
        self.harga_input.setPlaceholderText("Rp 0")
        self.harga_input.setValidator(QDoubleValidator(0.0, 999999999.0, 2))
        
        self.stok_input = QLineEdit()
        self.stok_input.setPlaceholderText("0")
        self.stok_input.setValidator(QIntValidator(0, 100000))
        
        right_form.addRow("Harga (Rp):", self.harga_input)
        right_form.addRow("Stok Awal:", self.stok_input)
        
        input_layout.addLayout(left_form)
        input_layout.addLayout(right_form)
        form_layout_main.addLayout(input_layout)
        
        # Action buttons
        style = StyleManager()
        
        self.btn_simpan = QPushButton("Simpan (Ctrl+S)")
        self.btn_simpan.setStyleSheet(style.get_button_style('success'))
        self.btn_simpan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_simpan.clicked.connect(self.simpan_produk)
        
        self.btn_batal = QPushButton("Reset (Ctrl+N)")
        self.btn_batal.setStyleSheet(style.get_button_style('default'))
        self.btn_batal.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_batal.clicked.connect(self.reset_form)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_simpan)
        btn_layout.addWidget(self.btn_batal)
        form_layout_main.addLayout(btn_layout)
        
        layout.addWidget(form_frame)
        
        # Search
        search_layout = QHBoxLayout()
        
        lbl_cari = QLabel("🔍 Cari Produk:")
        
        self.input_cari = QLineEdit()
        self.input_cari.setPlaceholderText("Ketik nama produk... (Ctrl+F)")
        self.input_cari.textChanged.connect(self.cari_produk)
        
        lbl_tip = QLabel("F2=Edit | Del=Hapus | ←→=Form↔Table")
        lbl_tip.setStyleSheet("color: #777; font-size: 11px; font-style: italic;")
        
        search_layout.addWidget(lbl_cari)
        search_layout.addWidget(self.input_cari)
        search_layout.addWidget(lbl_tip)
        
        layout.addLayout(search_layout)
        
        # Table
        self.table = SmartTable(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Barcode", "Nama", "Harga", "Stok"])
        self.table.setColumnHidden(0, True)
        self.table.stretch_column(2)
        self.table.set_column_width(1, 120)
        self.table.set_column_width(3, 120)
        self.table.set_column_width(4, 80)
        self.table.itemClicked.connect(self.isi_form_dari_tabel)
        
        layout.addWidget(self.table)
        
        self.barcode_input.setFocus()
    
    def setup_navigation(self):
        """
        SmartNavigation setup:
        - Manual navigation untuk form (no grid)
        - Memory navigation Form ↔ Table
        """
        
        # FORM INPUTS - Manual navigation
        # Barcode
        self.register_navigation(self.barcode_input, {
            Qt.Key.Key_Return: self.nama_input,
            Qt.Key.Key_Down: self.nama_input,
            Qt.Key.Key_Right: self.harga_input,
        })
        
        # Nama
        self.register_navigation(self.nama_input, {
            Qt.Key.Key_Return: self.harga_input,
            Qt.Key.Key_Down: self.btn_simpan,
            Qt.Key.Key_Up: self.barcode_input,
            Qt.Key.Key_Right: self.stok_input,
        })
        
        # Harga
        self.register_navigation(self.harga_input, {
            Qt.Key.Key_Return: self.stok_input,
            Qt.Key.Key_Down: self.stok_input,
            Qt.Key.Key_Up: self.barcode_input,
            Qt.Key.Key_Left: self.barcode_input,
        })
        
        # Stok
        self.register_navigation(self.stok_input, {
            Qt.Key.Key_Return: self.btn_simpan,
            Qt.Key.Key_Down: self.btn_batal,
            Qt.Key.Key_Up: self.harga_input,
            Qt.Key.Key_Left: self.nama_input,
        })
        
        # BUTTONS
        self.register_navigation(self.btn_simpan, {
            Qt.Key.Key_Return: self.simpan_produk,
            Qt.Key.Key_Up: self.nama_input,
            Qt.Key.Key_Right: self.btn_batal,
            Qt.Key.Key_Down: self.input_cari
        })
        
        self.register_navigation(self.btn_batal, {
            Qt.Key.Key_Return: self.reset_form,
            Qt.Key.Key_Up: self.stok_input,
            Qt.Key.Key_Left: self.btn_simpan,
            Qt.Key.Key_Down: self.input_cari
        })
        
        # SEARCH
        self.register_navigation(self.input_cari, {
            Qt.Key.Key_Return: lambda: self._go_to_table(self.input_cari),
            Qt.Key.Key_Down: lambda: self._go_to_table(self.input_cari),
            Qt.Key.Key_Up: self.btn_simpan
        })
        
        # TABLE
        self.register_table_callbacks(self.table, {
            'edit': self.isi_form_dari_tabel,
            'delete': self.hapus_produk,
            'focus_up': self.input_cari,
            'focus_down': self.btn_simpan
        })
        
        self.register_navigation(self.table, {
            Qt.Key.Key_Left: self._back_to_form
        })
        
    # Memory navigation helpers
    def _go_to_table(self, from_widget):
        """Jump ke table, ingat posisi form"""
        self.last_form_widget = from_widget
        self.focus_table_first_row(self.table)
    
    def _back_to_form(self):
        """Kembali ke form widget terakhir"""
        if self.last_form_widget:
            self.last_form_widget.setFocus()
            if hasattr(self.last_form_widget, 'selectAll'):
                self.last_form_widget.selectAll()
        else:
            self.barcode_input.setFocus()
    
    # Search
    def cari_produk(self):
        """Real-time search"""
        keyword = self.input_cari.text().strip()
        
        if not keyword:
            self.muat_produk()
            return
        
        hasil = cari_produk_by_nama_partial(keyword)
        self.tampilkan_data_di_tabel(hasil)
    
    # Data operations
    def muat_produk(self):
        """Load all products"""
        data = semua_produk()
        self.tampilkan_data_di_tabel(data)
    
    def tampilkan_data_di_tabel(self, data_list):
        """Display products in table"""
        self.table.clear_table()
        
        from PyQt6.QtWidgets import QTableWidgetItem
        
        for row, (id_produk, barcode, nama, harga, stok) in enumerate(data_list):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(id_produk)))
            self.table.setItem(row, 1, QTableWidgetItem(barcode))
            self.table.setItem(row, 2, QTableWidgetItem(nama))
            self.table.setItem(row, 3, QTableWidgetItem(f"Rp {int(harga):,}"))
            self.table.setItem(row, 4, QTableWidgetItem(str(stok)))
    
    def isi_form_dari_tabel(self):
        """Load product to form (F2/Enter)"""
        row = self.table.currentRow()
        if row < 0:
            return
        
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
        self.btn_simpan.setText("Update (Ctrl+S)")
        
        style = StyleManager()
        self.btn_simpan.setStyleSheet(style.get_button_style('warning'))
        
        self.barcode_input.setFocus()
    
    def reset_form(self):
        """Reset form (Ctrl+N)"""
        self.clear_form(
            self.barcode_input,
            self.nama_input,
            self.harga_input,
            self.stok_input,
            self.input_cari
        )
        
        self.id_produk_diedit = None
        self.btn_simpan.setText("Simpan (Ctrl+S)")
        
        style = StyleManager()
        self.btn_simpan.setStyleSheet(style.get_button_style('success'))
        
        self.table.clearSelection()
        self.barcode_input.setFocus()
    
    def simpan_produk(self):
        """Save or update product (Ctrl+S)"""
        barcode = self.barcode_input.text().strip()
        nama = self.nama_input.text().strip()
        harga_str = self.harga_input.text().strip().replace(".", "")
        stok_str = self.stok_input.text().strip()
        
        if not barcode or not nama or not harga_str:
            self.show_warning("Error", "Barcode, Nama, dan Harga wajib diisi.")
            return
        
        try:
            harga = float(harga_str)
            stok = int(stok_str) if stok_str else 0
        except ValueError:
            self.show_warning("Error", "Harga dan Stok harus angka.")
            return
        
        username = getattr(self, 'current_user', 'admin')
        
        if self.id_produk_diedit:
            update_produk_dengan_log(
                self.id_produk_diedit, barcode, nama, harga, stok, username
            )
            self.show_success("Berhasil", "Produk berhasil diupdate.")
        else:
            tambah_produk_dengan_log(barcode, nama, harga, stok, username)
            self.show_success("Berhasil", "Produk baru ditambahkan.")
        
        self.reset_form()
        self.muat_produk()
    
    def simpan(self):
        """Alias untuk Ctrl+S"""
        self.simpan_produk()
    
    def hapus_produk(self):
        """Delete product (Delete key)"""
        row = self.table.currentRow()
        if row < 0:
            self.show_warning("Pilih Produk", "Pilih produk di tabel dulu.")
            return
        
        nama = self.table.item(row, 2).text()
        id_produk = self.table.item(row, 0).text()
        
        if not self.confirm_action("Konfirmasi Hapus", f"Yakin ingin menghapus '{nama}'?"):
            return
        
        username = getattr(self, 'current_user', 'admin')
        hapus_produk_dengan_log(id_produk, username)
        
        self.muat_produk()
        self.reset_form()
    
    def handle_escape(self) -> bool:
        """ESC dengan konfirmasi jika ada perubahan"""
        if self.id_produk_diedit or self.barcode_input.text().strip():
            if self.confirm_action("Keluar", "Ada perubahan belum disimpan. Tetap keluar?"):
                self.close()
                return True
            return False
        else:
            self.close()
            return True