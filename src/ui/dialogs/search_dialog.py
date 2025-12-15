"""
Search Product Dialog
=====================
Dialog untuk mencari barang manual (bukan scan barcode)
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, QEvent
from src.database import cari_produk_by_nama_partial, semua_produk

class SearchDialog(QDialog):
    """
    Dialog cari barang dengan live search
    
    Returns:
        accepted: bool - True jika user pilih barang
        selected_barcode: str - Barcode barang yang dipilih
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.selected_barcode = None
        
        self.setup_ui()
        
        # Window properties
        self.setWindowTitle("Cari Barang Manual")
        self.setGeometry(200, 200, 700, 500)
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Search Bar
        search_layout = QHBoxLayout()
        
        self.input_cari = QLineEdit()
        self.input_cari.setPlaceholderText("Ketik nama barang... (Kosong = Tampilkan Semua)")
        self.input_cari.textChanged.connect(self.cari_data)
        self.input_cari.installEventFilter(self)
        
        btn_cari = QPushButton("Cari")
        btn_cari.setFixedWidth(80)
        btn_cari.clicked.connect(self.cari_data)
        
        search_layout.addWidget(self.input_cari)
        search_layout.addWidget(btn_cari)
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Barcode", "Nama", "Harga", "Stok"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.itemActivated.connect(self.pilih_barang)
        self.table.installEventFilter(self)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Info
        layout.addWidget(QLabel("Gunakan Panah Bawah untuk ke tabel, Enter untuk memilih."))
        
        # Initial focus & load data
        self.input_cari.setFocus()
        self.cari_data()
    
    def eventFilter(self, obj, event):
        """Handle keyboard navigation"""
        if event.type() == QEvent.Type.KeyPress:
            # Input Cari: Down = pindah ke tabel
            if obj == self.input_cari and event.key() == Qt.Key.Key_Down:
                if self.table.rowCount() > 0:
                    self.table.setFocus()
                    self.table.selectRow(0)
                return True
            
            # Tabel: ESC/Up = balik ke input
            elif obj == self.table:
                if event.key() == Qt.Key.Key_Escape:
                    self.input_cari.setFocus()
                    return True
                if event.key() == Qt.Key.Key_Up and self.table.currentRow() == 0:
                    self.input_cari.setFocus()
                    return True
        
        return super().eventFilter(obj, event)
    
    def cari_data(self):
        """Search products by keyword"""
        keyword = self.input_cari.text().strip()
        
        if not keyword:
            hasil = semua_produk()
        else:
            hasil = cari_produk_by_nama_partial(keyword)
        
        self.table.setRowCount(0)
        
        for row, (id_prod, barcode, nama, harga, stok) in enumerate(hasil):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(barcode))
            self.table.setItem(row, 1, QTableWidgetItem(nama))
            self.table.setItem(row, 2, QTableWidgetItem(f"Rp {int(harga):,}"))
            self.table.setItem(row, 3, QTableWidgetItem(str(stok)))
    
    def pilih_barang(self):
        """User pilih barang dari tabel"""
        row = self.table.currentRow()
        if row >= 0:
            self.selected_barcode = self.table.item(row, 0).text()
            self.accept()
    
    def keyPressEvent(self, event):
        """Handle ESC key"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)