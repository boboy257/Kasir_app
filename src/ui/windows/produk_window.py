"""
Produk Window - REFACTORED VERSION
===================================
Menggunakan BaseWindow untuk konsistensi
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
    QAbstractItemView, QFormLayout, QFrame
)
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QIntValidator, QDoubleValidator

from src.ui.base.base_window import BaseWindow
from src.ui.base.style_manager import StyleManager
from src.database import (
    tambah_produk_dengan_log, semua_produk, cari_produk_by_id,
    update_produk_dengan_log, hapus_produk_dengan_log,
    cari_produk_by_nama_partial
)

class ProdukWindow(BaseWindow):
    """
    Window untuk manajemen produk (CRUD)
    
    Features:
    - Tambah produk baru
    - Edit produk existing
    - Hapus produk
    - Search produk by nama
    - F2 untuk edit, Delete untuk hapus
    """
    
    def __init__(self):
        super().__init__()
        
        self.id_produk_diedit = None
        
        self.setup_ui()
        self.setup_navigation()
        
        # Window properties
        self.setWindowTitle("Manajemen Produk")
        self.setGeometry(100, 100, 1000, 650)
        
        # Load data
        self.muat_produk()
    
    def setup_ui(self):
        """Setup UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # ===== FORM CONTAINER =====
        form_frame = QFrame()
        form_frame.setStyleSheet(
            "background-color: #181818; border-radius: 10px; border: 1px solid #333;"
        )
        form_layout_main = QVBoxLayout(form_frame)
        form_layout_main.setContentsMargins(20, 20, 20, 20)
        
        lbl_judul = QLabel("📦 Input / Edit Produk")
        lbl_judul.setStyleSheet("font-size: 16px; color: #00E5FF; margin-bottom: 10px;")
        form_layout_main.addWidget(lbl_judul)
        
        # Form Layout (2 columns)
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
        btn_layout = QHBoxLayout()
        
        style = StyleManager()
        
        self.btn_simpan = QPushButton("Simpan Produk")
        self.btn_simpan.setStyleSheet(style.get_button_style('success'))
        self.btn_simpan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_simpan.clicked.connect(self.simpan_produk)
        
        self.btn_batal = QPushButton("Reset Form")
        self.btn_batal.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_batal.clicked.connect(self.reset_form)
        
        btn_layout.addWidget(self.btn_simpan)
        btn_layout.addWidget(self.btn_batal)
        form_layout_main.addLayout(btn_layout)
        
        layout.addWidget(form_frame)
        
        # ===== SEARCH & TABLE =====
        search_layout = QHBoxLayout()
        
        lbl_cari = QLabel("🔍 Cari Produk:")
        
        self.input_cari = QLineEdit()
        self.input_cari.setPlaceholderText("Ketik nama produk...")
        self.input_cari.textChanged.connect(self.cari_produk)
        
        lbl_tip = QLabel("Tips: Enter=Edit, Del=Hapus, Ctrl+Bawah=Tabel")
        lbl_tip.setStyleSheet("color: #777; font-size: 11px; font-style: italic;")
        
        search_layout.addWidget(lbl_cari)
        search_layout.addWidget(self.input_cari)
        search_layout.addWidget(lbl_tip)
        
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Barcode", "Nama", "Harga", "Stok"])
        self.table.setColumnHidden(0, True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget { alternate-background-color: #252525; }")
        self.table.itemClicked.connect(self.isi_form_dari_tabel)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.table)
        
        # Focus awal
        self.barcode_input.setFocus()
    
    def setup_navigation(self):
        """Setup keyboard navigation"""
        
        # Barcode: Right=Harga, Down/Enter=Nama
        self.register_navigation(self.barcode_input, {
            Qt.Key.Key_Right: self.harga_input,
            Qt.Key.Key_Down: self.nama_input,
            Qt.Key.Key_Return: self.nama_input
        })
        
        # Harga: Left=Barcode, Down/Enter=Stok
        self.register_navigation(self.harga_input, {
            Qt.Key.Key_Left: self.barcode_input,
            Qt.Key.Key_Down: self.stok_input,
            Qt.Key.Key_Return: lambda: (self.stok_input.setFocus(), self.stok_input.selectAll())
        })
        
        # Nama: Up=Barcode, Right=Stok, Down=Simpan
        self.register_navigation(self.nama_input, {
            Qt.Key.Key_Up: self.barcode_input,
            Qt.Key.Key_Right: self.stok_input,
            Qt.Key.Key_Down: self.btn_simpan,
            Qt.Key.Key_Return: lambda: (self.harga_input.setFocus(), self.harga_input.selectAll())
        })
        
        # Stok: Up=Harga, Left=Nama, Down=Batal, Enter=Simpan
        self.register_navigation(self.stok_input, {
            Qt.Key.Key_Up: self.harga_input,
            Qt.Key.Key_Left: self.nama_input,
            Qt.Key.Key_Down: self.btn_batal,
            Qt.Key.Key_Return: self.btn_simpan
        })
        
        # Button Simpan
        self.register_navigation(self.btn_simpan, {
            Qt.Key.Key_Up: self.nama_input,
            Qt.Key.Key_Right: self.btn_batal,
            Qt.Key.Key_Down: self.input_cari,
            Qt.Key.Key_Return: self.simpan_produk
        })
        
        # Button Batal
        self.register_navigation(self.btn_batal, {
            Qt.Key.Key_Left: self.btn_simpan,
            Qt.Key.Key_Up: self.stok_input,
            Qt.Key.Key_Down: self.input_cari,
            Qt.Key.Key_Return: self.reset_form
        })
        
        # Input Cari: Enter/Down=Table
        self.register_navigation(self.input_cari, {
            Qt.Key.Key_Return: lambda: self.focus_table_first_row(self.table),
            Qt.Key.Key_Down: lambda: self.focus_table_first_row(self.table),
            Qt.Key.Key_Up: self.btn_simpan
        })
    
    def eventFilter(self, obj, event):
        """Handle special shortcuts"""
        if event.type() == QEvent.Type.KeyPress:
            
            # Ctrl+Down: Jump to table
            if (event.modifiers() == Qt.KeyboardModifier.ControlModifier and
                event.key() == Qt.Key.Key_Down):
                if self.table.rowCount() > 0:
                    self.focus_table_first_row(self.table)
                return True
            
            # Ctrl+Up: Back to barcode
            if (event.modifiers() == Qt.KeyboardModifier.ControlModifier and
                event.key() == Qt.Key.Key_Up):
                self.barcode_input.setFocus()
                return True
            
            # Table shortcuts
            if obj == self.table:
                # Up di baris 0 = balik ke search
                if event.key() == Qt.Key.Key_Up and self.table.currentRow() <= 0:
                    self.input_cari.setFocus()
                    return True
                
                # F2 atau Enter = Edit
                if event.key() == Qt.Key.Key_F2 or event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self.isi_form_dari_tabel()
                    return True
                
                # Delete = Hapus
                if event.key() == Qt.Key.Key_Delete:
                    self.hapus_produk()
                    return True
        
        return super().eventFilter(obj, event)
    
    # ========== SEARCH ==========
    
    def cari_produk(self):
        """Real-time search produk"""
        keyword = self.input_cari.text().strip()
        
        if not keyword:
            self.muat_produk()
            return
        
        hasil = cari_produk_by_nama_partial(keyword)
        self.tampilkan_data_di_tabel(hasil)
    
    # ========== DATA OPERATIONS ==========
    
    def muat_produk(self):
        """Load semua produk"""
        data = semua_produk()
        self.tampilkan_data_di_tabel(data)
    
    def tampilkan_data_di_tabel(self, data_list):
        """Display products in table"""
        self.table.setRowCount(0)
        
        for row, (id_produk, barcode, nama, harga, stok) in enumerate(data_list):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(id_produk)))
            self.table.setItem(row, 1, QTableWidgetItem(barcode))
            self.table.setItem(row, 2, QTableWidgetItem(nama))
            self.table.setItem(row, 3, QTableWidgetItem(f"Rp {int(harga):,}"))
            self.table.setItem(row, 4, QTableWidgetItem(str(stok)))
    
    def isi_form_dari_tabel(self):
        """Load product from table to form"""
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
        self.btn_simpan.setText("Update Produk")
        
        style = StyleManager()
        self.btn_simpan.setStyleSheet(style.get_button_style('warning'))
        
        self.barcode_input.setFocus()
    
    def reset_form(self):
        """Reset form to initial state"""
        self.clear_form(
            self.barcode_input,
            self.nama_input,
            self.harga_input,
            self.stok_input,
            self.input_cari
        )
        
        self.id_produk_diedit = None
        self.btn_simpan.setText("Simpan Produk")
        
        style = StyleManager()
        self.btn_simpan.setStyleSheet(style.get_button_style('success'))
        
        self.table.clearSelection()
        self.barcode_input.setFocus()
    
    def simpan_produk(self):
        """Save or update product"""
        barcode = self.barcode_input.text().strip()
        nama = self.nama_input.text().strip()
        harga_str = self.harga_input.text().strip().replace(".", "")
        stok_str = self.stok_input.text().strip()
        
        # Validasi
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
        
        # Update mode
        if self.id_produk_diedit:
            update_produk_dengan_log(
                self.id_produk_diedit, barcode, nama, harga, stok, username
            )
            self.show_success("Berhasil", "Produk berhasil diupdate.")
        
        # Insert mode
        else:
            tambah_produk_dengan_log(barcode, nama, harga, stok, username)
            self.show_success("Berhasil", "Produk baru ditambahkan.")
        
        self.reset_form()
        self.muat_produk()
    
    def hapus_produk(self):
        """Delete selected product"""
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