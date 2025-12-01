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
    def __init__(self, on_logout=None):
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
        self.lbl_judul = QLabel("Menu Utama Aplikasi Kasir")
        self.lbl_judul.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_judul.setStyleSheet("color: #ffffff; font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        main_layout.addWidget(self.lbl_judul)

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

       # TOMBOL LOGOUT
        self.btn_logout = QPushButton("Logout / Keluar")
        self.btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f; 
                color: white; 
                border: 2px solid #b71c1c; 
                padding: 10px; 
                border-radius: 5px;
                font-weight: bold;
                outline: none;
            }
            QPushButton:focus {
                border: 2px solid #ff5252; /* Efek fokus logout */
                background-color: #c62828;
            }
        """)
        self.btn_logout.clicked.connect(self.close)
        
        # TOMBOL LOGOUT
        self.btn_logout = QPushButton("Logout / Keluar")
        self.btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f; 
                color: white; 
                border: 2px solid #b71c1c; 
                padding: 10px; 
                border-radius: 5px;
                font-weight: bold;
                outline: none;
            }
            QPushButton:focus {
                border: 2px solid #ff5252; /* Efek fokus logout */
                background-color: #c62828;
            }
        """)
        if on_logout:
            self.btn_logout.clicked.connect(on_logout)
        else:
            self.btn_logout.clicked.connect(self.close)
        
        # [PERBAIKAN 1] Agar tombol logout bisa di-Enter
        self.btn_logout.setAutoDefault(True)
        self.btn_logout.setDefault(False)
        self.btn_logout.installEventFilter(self) # Masukkan ke event filter juga biar nyambung navigasinya
        self.btn_logout.setProperty("is_logout", True) # Penanda khusus

        main_layout.addWidget(self.btn_logout)

        if self.buttons:
            self.buttons[0].setFocus()
            
    # --- LOGIKA HAK AKSES (ROLE) ---
    def set_user_role(self, username, role):
        """Mengatur tampilan berdasarkan role user"""
        self.current_user = username
        self.current_role = role
        
        # Update Judul
        role_display = "ADMINISTRATOR" if role == "admin" else "KASIR"
        self.lbl_judul.setText(f"Halo, {username} ({role_display})")
        self.setWindowTitle(f"Sistem Kasir Pro - {role_display}")

        # Logika Kunci Tombol
        if role == "kasir":
            tombol_dilarang = [1, 2, 3, 5, 6, 7]
            
            for index in tombol_dilarang:
                self.buttons[index].setVisible(False) # Matikan tombol
        else:
            # Jika Admin, aktifkan semua
            for btn in self.buttons:
                btn.setVisible(True)
                
    # --- LOGIKA NAVIGASI KEYBOARD CERDAS ---
    def eventFilter(self, obj, event):
        # Kita cek apakah kejadiannya adalah Penekanan Tombol Keyboard
        if event.type() == QEvent.Type.KeyPress:
            # Ambil index tombol saat ini (0 s/d 7)
            current_index = obj.property("index")
            is_logout = obj.property("is_logout")
            
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
                    target_bawah = current_index + 4
                    
                    if current_index >= 4:
                        self.btn_logout.setFocus()
                        return True
                    elif target_bawah < len(self.buttons) and not self.buttons[target_bawah].isVisible():
                        # Kasus khusus Kasir: Tombol bawahnya hilang, jadi langsung ke logout
                        self.btn_logout.setFocus()
                        return True
                    elif target_bawah < len(self.buttons):
                        next_index = target_bawah
                
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

            # --- NAVIGASI TOMBOL LOGOUT ---
            elif is_logout:
                # ATAS -> Cari tombol aktif paling bawah
                if event.key() == Qt.Key.Key_Up:
                    # Kita cari dari belakang (index 7 mundur ke 0)
                    for i in range(len(self.buttons) - 1, -1, -1):
                        if self.buttons[i].isVisible():
                            self.buttons[i].setFocus()
                            return True
                
                # ENTER
                elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    obj.click()
                    return True
                
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