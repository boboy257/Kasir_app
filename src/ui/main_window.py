from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from src.ui.kasir_window import KasirWindow
from src.ui.produk_window import ProdukWindow
from src.ui.kelola_db_window import KelolaDBWindow
from src.ui.laporan_window import LaporanWindow 

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

        layout.addWidget(self.btn_kasir)
        layout.addWidget(self.btn_produk)
        layout.addWidget(self.btn_kelola_db)
        layout.addWidget(self.btn_laporan)

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