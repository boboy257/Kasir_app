from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLabel, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, QEvent # [TAMBAHAN] Import QEvent
from src.database import create_connection

class StokRendahWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Laporan Stok Rendah")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # --- STYLE DARK MODE ---
        central_widget.setStyleSheet("""
            QWidget { background-color: #121212; color: #e0e0e0; font-family: 'Segoe UI'; font-size: 13px; }
            QTableWidget { background-color: #1E1E1E; gridline-color: #333; border: 1px solid #333; }
            QHeaderView::section { background-color: #252525; color: white; padding: 8px; border: none; font-weight: bold; }
            QPushButton { background-color: #4CAF50; color: white; border: none; padding: 8px 15px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:focus { border: 2px solid #ffffff; }
            QLabel { font-weight: bold; color: #FF9800; font-size: 14px; }
        """)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)

        # Label info
        label_info = QLabel("⚠️ Produk dengan stok di bawah 5:")
        layout.addWidget(label_info)

        # Tombol refresh
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh Data")
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.muat_stok_rendah)
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Tabel laporan stok rendah
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Barcode", "Nama", "Stok"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget { alternate-background-color: #252525; }")
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch) # Nama melar
        
        layout.addWidget(self.table)

        # Muat data awal
        self.muat_stok_rendah()
        
        # [PENTING] Pasang telinga ESC
        self.installEventFilter(self)

    # [LOGIKA ESC]
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Escape:
            self.close()
            return True
        return super().eventFilter(obj, event)

    def muat_stok_rendah(self):
        """Muat produk dengan stok rendah (stok < 5)"""
        self.table.setRowCount(0)
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, barcode, nama, stok 
            FROM produk 
            WHERE stok < 5 
            ORDER BY stok ASC
        """)
        hasil = cursor.fetchall()
        conn.close()

        for row, (id_produk, barcode, nama, stok) in enumerate(hasil):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(id_produk)))
            self.table.setItem(row, 1, QTableWidgetItem(barcode))
            self.table.setItem(row, 2, QTableWidgetItem(nama))
            
            # Warna Merah untuk stok
            item_stok = QTableWidgetItem(str(stok))
            item_stok.setForeground(Qt.GlobalColor.red)
            item_stok.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, item_stok)

    def set_current_user(self, username):
        self.current_user = username