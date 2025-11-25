from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from src.ui.kasir_window import KasirWindow
from src.ui.produk_window import ProdukWindow
from src.ui.kelola_db_window import KelolaDBWindow
from src.ui.laporan_window import LaporanWindow
from src.ui.login_window import LoginWindow
from src.ui.stok_rendah_window import StokRendahWindow  
from src.ui.generate_barcode_window import GenerateBarcodeWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplikasi Kasir")
        self.setGeometry(100, 100, 400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.btn_kasir = QPushButton("Mode Kasir")
        self.btn_produk = QPushButton("Input Produk")
        self.btn_kelola_db = QPushButton("Kelola Database")

        self.btn_kasir.clicked.connect(self.buka_kasir)
        self.btn_produk.clicked.connect(self.buka_produk)
        self.btn_kelola_db.clicked.connect(self.buka_kelola_db)
        self.btn_laporan = QPushButton("Laporan Penjualan")
        self.btn_laporan.clicked.connect(self.buka_laporan)
        self.btn_stok_rendah = QPushButton("Laporan Stok Rendah")
        self.btn_stok_rendah.clicked.connect(self.buka_stok_rendah)
        self.btn_generate_barcode = QPushButton("Generate Barcode")
        self.btn_generate_barcode.clicked.connect(self.buka_generate_barcode)

        layout.addWidget(self.btn_kasir)
        layout.addWidget(self.btn_produk)
        layout.addWidget(self.btn_kelola_db)
        layout.addWidget(self.btn_laporan)
        layout.addWidget(self.btn_stok_rendah)
        layout.addWidget(self.btn_generate_barcode)

    def buka_kasir(self):
        self.kasir_window = KasirWindow()
        self.kasir_window.show()

    def buka_produk(self):
        self.produk_window = ProdukWindow()
        self.produk_window.show()

    def buka_kelola_db(self):
        self.kelola_window = KelolaDBWindow()
        self.kelola_window.show()

    def buka_laporan(self):
        self.laporan_window = LaporanWindow()
        self.laporan_window.show()
    
    def buka_stok_rendah(self):
        self.stok_rendah_window = StokRendahWindow()
        self.stok_rendah_window.show()

    def buka_generate_barcode(self):
        self.generate_barcode_window = GenerateBarcodeWindow()
        self.generate_barcode_window.show()