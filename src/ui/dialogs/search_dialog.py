"""
Search Product Dialog - CLEAN VERSION

"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, QEvent
from src.ui.base.style_manager import StyleManager
from src.database import cari_produk_by_nama_partial, semua_produk

class SearchDialog(QDialog):
    """Dialog cari barang - Clean & Consistent"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.selected_barcode = None
        
        self.setup_ui()
        
        self.setWindowTitle("Cari Barang Manual")
        self.setGeometry(200, 200, 900, 500)
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        style = StyleManager()
        
        # Search Bar
        search_layout = QHBoxLayout()
        
        self.input_cari = QLineEdit()
        self.input_cari.setPlaceholderText("Ketik nama barang... (Kosong = Tampilkan Semua)")
        self.input_cari.setMinimumHeight(40)
        self.input_cari.textChanged.connect(self.cari_data)
        self.input_cari.installEventFilter(self)
        
        # ✅ Button pakai StyleManager (konsisten!)
        btn_cari = QPushButton("🔍 Cari")
        btn_cari.setStyleSheet(style.get_button_style_fixed('primary', 100, 40))
        btn_cari.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cari.clicked.connect(self.cari_data)
        
        search_layout.addWidget(self.input_cari)
        search_layout.addWidget(btn_cari)
        layout.addLayout(search_layout)
        
        # ✅ Table dengan kolom No (5 kolom)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["No", "Barcode", "Nama", "Harga", "Stok"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.itemActivated.connect(self.pilih_barang)
        self.table.installEventFilter(self)
        
        # ✅ Column widths optimal
        header = self.table.horizontalHeader()
        self.table.setColumnWidth(0, 60)   # No
        self.table.setColumnWidth(1, 150)  # Barcode
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Nama
        self.table.setColumnWidth(3, 120)  # Harga
        self.table.setColumnWidth(4, 80)   # Stok
        
        layout.addWidget(self.table)
        
        # Info
        lbl_info = QLabel("↓ = Tabel | Enter = Pilih | ESC = Batal")
        lbl_info.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(lbl_info)
        
        self.input_cari.setFocus()
        self.cari_data()
    
    def eventFilter(self, obj, event):
        """Handle keyboard navigation"""
        if event.type() == QEvent.Type.KeyPress:
            if obj == self.input_cari and event.key() == Qt.Key.Key_Down:
                if self.table.rowCount() > 0:
                    self.table.setFocus()
                    self.table.selectRow(0)
                return True
            
            elif obj == self.table:
                if event.key() == Qt.Key.Key_Escape:
                    self.input_cari.setFocus()
                    return True
                if event.key() == Qt.Key.Key_Up and self.table.currentRow() == 0:
                    self.input_cari.setFocus()
                    return True
        
        return super().eventFilter(obj, event)
    
    def cari_data(self):
        """Search products"""
        keyword = self.input_cari.text().strip()
        
        if not keyword:
            hasil = semua_produk()
        else:
            hasil = cari_produk_by_nama_partial(keyword)
        
        self.table.setRowCount(0)
        
        for row, (id_prod, barcode, nama, harga, stok) in enumerate(hasil):
            self.table.insertRow(row)
            
            # Kolom No
            item_no = QTableWidgetItem(str(row + 1))
            item_no.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, item_no)
            
            # Data produk
            self.table.setItem(row, 1, QTableWidgetItem(barcode))
            self.table.setItem(row, 2, QTableWidgetItem(nama))
            self.table.setItem(row, 3, QTableWidgetItem(f"Rp {int(harga):,}"))
            self.table.setItem(row, 4, QTableWidgetItem(str(stok)))
    
    def pilih_barang(self):
        """User pilih barang"""
        row = self.table.currentRow()
        if row >= 0:
            self.selected_barcode = self.table.item(row, 1).text()
            self.accept()
    
    def keyPressEvent(self, event):
        """Handle ESC key"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)