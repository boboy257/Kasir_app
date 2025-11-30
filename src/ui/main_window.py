from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton, QGridLayout, QLabel,
    QSizePolicy
)
from PyQt6.QtCore import QSize, Qt, QEvent
# Import window lainnya
from src.ui.kasir_window import KasirWindow
from src.ui.produk_window import ProdukWindow
from src.ui.kelola_db_window import KelolaDBWindow
from src.ui.laporan_window import LaporanWindow
from src.ui.stok_rendah_window import StokRendahWindow
from src.ui.generate_barcode_window import GenerateBarcodeWindow
from src.ui.manajemen_user_window import ManajemenUserWindow
from src.ui.log_aktivitas_window import LogAktivitasWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistem Kasir Pro")
        self.setGeometry(100, 100, 900, 600)

        # --- SETUP UI DASAR (DARK MODE) ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background-color: #121212;") 

        # Layout Utama
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        # 1. JUDUL APLIKASI
        lbl_judul = QLabel("Menu Utama Aplikasi Kasir")
        lbl_judul.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_judul.setStyleSheet("color: #ffffff; font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        main_layout.addWidget(lbl_judul)

        # 2. CONTAINER TOMBOL (GRID)
        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
        grid_layout.setSpacing(20) 
        
        # Konfigurasi Tombol
        buttons_config = [
            ("Mode Kasir", self.buka_kasir),
            ("Input Produk", self.buka_produk),
            ("Kelola Database", self.buka_kelola_db),
            ("Laporan Penjualan", self.buka_laporan),
            ("Cek Stok Rendah", self.buka_stok_rendah),
            ("Generate Barcode", self.buka_generate_barcode),
            ("Manajemen User", self.buka_manajemen_user),
            ("Log Aktivitas", self.buka_log_aktivitas)
        ]

        # Style Tombol Dark Mode
        btn_style = """
            QPushButton {
                background-color: #1E1E1E;
                color: #E0E0E0;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #333333;
                border-radius: 12px;
                padding: 15px;
                outline: none;
            }
            QPushButton:hover {
                background-color: #2D2D2D;
                border: 2px solid #555555;
            }
            QPushButton:focus {
                background-color: #252525;
                border: 2px solid #2196F3; /* Fokus Biru Menyala */
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #000000;
            }
        """

        self.buttons = []
        row = 0
        col = 0
        self.max_col = 4 # Kita simpan ini untuk logika navigasi

        for i, (text, handler) in enumerate(buttons_config):
            btn = QPushButton(text)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.setMinimumHeight(100)
            btn.setStyleSheet(btn_style)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Setting agar tombol merespon keyboard
            btn.setAutoDefault(True) 
            btn.setDefault(False)
            
            # [PENTING] Pasang Event Filter untuk menangkap tombol Panah
            btn.installEventFilter(self)
            
            # Simpan index tombol agar kita tahu posisinya
            btn.setProperty("index", i)

            btn.clicked.connect(handler)
            
            grid_layout.addWidget(btn, row, col)
            self.buttons.append(btn)

            col += 1
            if col >= self.max_col:
                col = 0
                row += 1

        main_layout.addWidget(grid_container)
        main_layout.addStretch()

        # Fokus awal
        if self.buttons:
            self.buttons[0].setFocus()

    # --- LOGIKA NAVIGASI KEYBOARD CERDAS ---
    def eventFilter(self, obj, event):
        # Kita cek apakah kejadiannya adalah Penekanan Tombol Keyboard
        if event.type() == QEvent.Type.KeyPress:
            # Ambil index tombol saat ini (0 s/d 7)
            current_index = obj.property("index")
            
            if current_index is not None:
                # Logika Pindah Fokus
                next_index = None
                
                # PANAH KANAN -> Index + 1
                if event.key() == Qt.Key.Key_Right:
                    if (current_index + 1) < len(self.buttons):
                        next_index = current_index + 1
                
                # PANAH KIRI -> Index - 1
                elif event.key() == Qt.Key.Key_Left:
                    if (current_index - 1) >= 0:
                        next_index = current_index - 1
                
                # PANAH BAWAH -> Index + 4 (Pindah baris ke bawah)
                elif event.key() == Qt.Key.Key_Down:
                    if (current_index + self.max_col) < len(self.buttons):
                        next_index = current_index + self.max_col
                
                # PANAH ATAS -> Index - 4 (Pindah baris ke atas)
                elif event.key() == Qt.Key.Key_Up:
                    if (current_index - self.max_col) >= 0:
                        next_index = current_index - self.max_col
                
                # TOMBOL ENTER -> Klik Tombol
                elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    obj.click()
                    return True

                # Eksekusi Pindah Fokus
                if next_index is not None:
                    self.buttons[next_index].setFocus()
                    return True # Berhenti di sini, jangan biarkan Qt melakukan hal lain

        return super().eventFilter(obj, event)

    # --- Fungsi Handler Tetap Sama ---
    def buka_kasir(self):
        self.kasir_window = KasirWindow()
        if hasattr(self, 'current_user'): self.kasir_window.set_current_user(self.current_user)
        self.kasir_window.show()

    def buka_produk(self):
        self.produk_window = ProdukWindow()
        if hasattr(self, 'current_user'): self.produk_window.set_current_user(self.current_user)
        self.produk_window.show()

    def buka_kelola_db(self):
        self.kelola_window = KelolaDBWindow()
        if hasattr(self, 'current_user'): self.kelola_window.set_current_user(self.current_user)
        self.kelola_window.show()

    def buka_laporan(self):
        self.laporan_window = LaporanWindow()
        if hasattr(self, 'current_user'): self.laporan_window.set_current_user(self.current_user)
        self.laporan_window.show()

    def buka_stok_rendah(self):
        self.stok_rendah_window = StokRendahWindow()
        if hasattr(self, 'current_user'): self.stok_rendah_window.set_current_user(self.current_user)
        self.stok_rendah_window.show()

    def buka_generate_barcode(self):
        self.generate_barcode_window = GenerateBarcodeWindow()
        if hasattr(self, 'current_user'): self.generate_barcode_window.set_current_user(self.current_user)
        self.generate_barcode_window.show()

    def buka_manajemen_user(self):
        self.manajemen_user_window = ManajemenUserWindow()
        if hasattr(self, 'current_user'): self.manajemen_user_window.set_current_user(self.current_user)
        self.manajemen_user_window.show()

    def buka_log_aktivitas(self):
        self.log_aktivitas_window = LogAktivitasWindow()
        if hasattr(self, 'current_user'): self.log_aktivitas_window.set_current_user(self.current_user)
        self.log_aktivitas_window.show()

    def set_current_user(self, username):
        self.current_user = username