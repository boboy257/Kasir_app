"""
Main Window - REFACTORED with SmartNavigation
==============================================
Dashboard + Menu Grid dengan full keyboard navigation
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QPushButton, QGridLayout, QLabel,
    QSizePolicy, QHBoxLayout, QFrame
)
from PyQt6.QtCore import Qt, QTimer

from src.ui.base.base_window import BaseWindow
from src.ui.base.style_manager import StyleManager
from src.database import get_info_dashboard

# Window imports
from src.ui.windows.kasir_window import KasirWindow
from src.ui.windows.produk_window import ProdukWindow
from src.ui.windows.kelola_db_window import KelolaDBWindow
from src.ui.windows.laporan_window import LaporanWindow
from src.ui.windows.stok_rendah_window import StokRendahWindow
from src.ui.windows.generate_barcode_window import GenerateBarcodeWindow
from src.ui.windows.manajemen_user_window import ManajemenUserWindow
from src.ui.windows.log_aktivitas_window import LogAktivitasWindow
from src.ui.windows.pengaturan_window import PengaturanWindow
from src.ui.windows.riwayat_hari_ini_window import RiwayatHariIniWindow


class MainWindow(BaseWindow):
    """
    Main window dengan SmartNavigation
    
    Layout:
    - Header: [Riwayat] [Settings] [Logout]
    - Dashboard: Info cards + Chart
    - Menu Grid: 4 columns x 2 rows
    """
    
    def __init__(self, on_logout=None):
        super().__init__()
        
        self.on_logout = on_logout
        self.current_role = None
        self.menu_buttons = []  # List of menu buttons untuk grid navigation
        self.header_buttons = []  # List of header buttons
        
        self.setup_ui()
        self.setup_navigation()  # ✨ SmartNavigation setup
        
        self.setWindowTitle("Sistem Kasir Pro")
        self.setGeometry(100, 100, 1000, 700)
        
        # Lazy load dashboard
        QTimer.singleShot(100, self.lazy_load_dashboard)
        
        # Setup help overlay
        self.setup_help_overlay(self.get_main_shortcuts())
    
    def setup_ui(self):
        """Setup UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background-color: #121212;")
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)
        
        # ========== HEADER ==========
        header_layout = QHBoxLayout()
        
        self.lbl_judul = QLabel("Dashboard")
        self.lbl_judul.setStyleSheet(
            "color: #ffffff; font-size: 24px; font-weight: bold;"
        )
        
        header_layout.addWidget(self.lbl_judul)
        header_layout.addStretch()
        
        # Header buttons
        style = StyleManager()
        
        self.btn_riwayat = QPushButton("📊 Riwayat Hari Ini")
        self.btn_riwayat.setFixedSize(150, 40)
        self.btn_riwayat.setStyleSheet(style.get_button_style('warning'))
        self.btn_riwayat.clicked.connect(self.buka_riwayat)
        
        self.btn_settings = QPushButton("⚙️ Pengaturan")
        self.btn_settings.setFixedSize(120, 40)
        self.btn_settings.setStyleSheet("""
            QPushButton { 
                background-color: #607D8B; color: white; 
                border-radius: 5px; font-weight: bold; 
            }
            QPushButton:hover { background-color: #546E7A; }
            QPushButton:focus { border: 2px solid #B0BEC5; }
        """)
        self.btn_settings.clicked.connect(self.buka_pengaturan)
        
        self.btn_logout = QPushButton("Logout")
        self.btn_logout.setFixedSize(100, 40)
        self.btn_logout.setStyleSheet(style.get_button_style('danger'))
        
        if self.on_logout:
            self.btn_logout.clicked.connect(self.on_logout)
        else:
            self.btn_logout.clicked.connect(self.close)
        
        # Simpan header buttons untuk navigation
        self.header_buttons = [self.btn_riwayat, self.btn_settings, self.btn_logout]
        
        header_layout.addWidget(self.btn_riwayat)
        header_layout.addWidget(self.btn_settings)
        header_layout.addWidget(self.btn_logout)
        main_layout.addLayout(header_layout)
        
        # ========== DASHBOARD AREA ==========
        self.dashboard_container = QWidget()
        self.dash_layout = QHBoxLayout(self.dashboard_container)
        self.dash_layout.setContentsMargins(0, 10, 0, 10)
        
        # Info Panel (Kiri)
        info_panel = QVBoxLayout()
        
        self.card_omset = QFrame()
        self.card_omset.setStyleSheet(
            "background-color: #1E1E1E; border-radius: 10px; border: 1px solid #333;"
        )
        card1_layout = QVBoxLayout(self.card_omset)
        self.lbl_omset_title = QLabel("Omset Hari Ini")
        self.lbl_omset_title.setStyleSheet("color: #aaa; font-size: 14px;")
        self.lbl_omset_value = QLabel("Loading...")
        self.lbl_omset_value.setStyleSheet(
            "color: #4CAF50; font-size: 28px; font-weight: bold;"
        )
        card1_layout.addWidget(self.lbl_omset_title)
        card1_layout.addWidget(self.lbl_omset_value)
        
        self.card_trx = QFrame()
        self.card_trx.setStyleSheet(
            "background-color: #1E1E1E; border-radius: 10px; border: 1px solid #333;"
        )
        card2_layout = QVBoxLayout(self.card_trx)
        self.lbl_trx_title = QLabel("Total Transaksi")
        self.lbl_trx_title.setStyleSheet("color: #aaa; font-size: 14px;")
        self.lbl_trx_value = QLabel("-")
        self.lbl_trx_value.setStyleSheet(
            "color: #2196F3; font-size: 28px; font-weight: bold;"
        )
        card2_layout.addWidget(self.lbl_trx_title)
        card2_layout.addWidget(self.lbl_trx_value)
        
        info_panel.addWidget(self.card_omset)
        info_panel.addWidget(self.card_trx)
        
        # Chart Container (Kanan)
        self.chart_container = QWidget()
        self.chart_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.chart_layout = QVBoxLayout(self.chart_container)
        
        self.dash_layout.addLayout(info_panel, 1)
        self.dash_layout.addWidget(self.chart_container, 2)
        
        main_layout.addWidget(self.dashboard_container)
        
        # ========== MENU GRID ==========
        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
        grid_layout.setSpacing(15)
        
        # Menu buttons configuration
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
        
        btn_style = """
            QPushButton {
                background-color: #1E1E1E; 
                color: #E0E0E0; 
                font-size: 14px; 
                font-weight: bold;
                border: 2px solid #333333; 
                border-radius: 10px; 
                padding: 10px; 
            }
            QPushButton:hover { 
                background-color: #2D2D2D; 
                border: 2px solid #555555; 
            }
            QPushButton:focus { 
                background-color: #252525; 
                border: 2px solid #2196F3; 
                color: #ffffff; 
            }
        """
        
        # Create grid (4 columns x 2 rows)
        self.menu_buttons = []
        row = 0
        col = 0
        max_col = 4
        
        for text, handler in buttons_config:
            btn = QPushButton(text)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.setMinimumHeight(80)
            btn.setStyleSheet(btn_style)
            btn.clicked.connect(handler)
            
            grid_layout.addWidget(btn, row, col)
            self.menu_buttons.append(btn)
            
            col += 1
            if col >= max_col:
                col = 0
                row += 1
        
        main_layout.addWidget(grid_container)
        
        # Focus awal ke header button pertama
        self.menu_buttons[0].setFocus()
    
    def setup_navigation(self):
        """
        ✨ SMART NAVIGATION SETUP
        
        Layout zones:
        1. Header buttons (1 row, 3 buttons)
        2. Dashboard (skip - read only)
        3. Menu grid (2 rows, 4 columns)
        """
        
        # ===== ZONE 1: HEADER BUTTONS (Circular Row) =====
        self.register_navigation_row(self.header_buttons, circular=True)
        
        # Header buttons: Enter = Click
        for i, btn in enumerate(self.header_buttons):
            target_menu = self.menu_buttons[i] if i < len(self.menu_buttons) else self.menu_buttons[0]
            
            self.register_navigation(btn, {
                Qt.Key.Key_Return: lambda b=btn: b.click(),
                Qt.Key.Key_Down: target_menu  # Turun sesuai posisi!
            })
        
        # ===== ZONE 2: MENU GRID (2D Navigation) =====
        # Organize buttons into grid structure
        menu_grid = [
            self.menu_buttons[0:4],  # Row 1: buttons 0-3
            self.menu_buttons[4:8],  # Row 2: buttons 4-7
        ]
        
        self.register_navigation_grid(menu_grid, circular=False)
        
        # Menu buttons: Enter = Click (semua button di grid)
        for btn in self.menu_buttons:
            self.register_navigation(btn, {
                Qt.Key.Key_Return: lambda b=btn: b.click()
            })
        
        # Row 1 mapping (first 4 menu buttons)
        menu_to_header_map = [
            (self.menu_buttons[0], self.btn_riwayat),    # Kasir → Riwayat
            (self.menu_buttons[1], self.btn_settings),   # Produk → Pengatura
            (self.menu_buttons[2], self.btn_logout),     # Kelola → Logout
            (self.menu_buttons[3], self.btn_logout),     # Laporan → Logout (fallback)
        ]

        for menu_btn, header_btn in menu_to_header_map:
            self.register_navigation(menu_btn, {
                Qt.Key.Key_Up: header_btn,
                Qt.Key.Key_Return: lambda b=menu_btn: b.click()
            })

        # Row 2 mapping (last 4 menu buttons)
        menu_to_header_map_row2 = [
            (self.menu_buttons[4], self.btn_riwayat),    # Stok → Riwayat
            (self.menu_buttons[5], self.btn_settings),   # Barcode → Pengatura
            (self.menu_buttons[6], self.btn_logout),     # User → Logout
            (self.menu_buttons[7], self.btn_logout),     # Log → Logout
        ]

        for menu_btn, header_btn in menu_to_header_map_row2:
            self.register_navigation(menu_btn, {
                Qt.Key.Key_Up: header_btn,
                Qt.Key.Key_Return: lambda b=menu_btn: b.click()
            })
        
        # ===== CUSTOM: Kasir Role Fix =====
        # Override untuk kasir yang cuma punya 2 menu visible
        # Akan di-update di set_user_role()
    
    # ========== USER ROLE MANAGEMENT ==========
    
    def set_user_role(self, username, role):
        """Set user role dan hide/show berdasarkan akses"""
        self.current_user = username
        self.current_role = role
        
        role_disp = "ADMINISTRATOR" if role == "admin" else "KASIR"
        self.lbl_judul.setText(f"Dashboard - {username} ({role_disp})")
        
        if role == "kasir":
            # Kasir: Hanya Mode Kasir
            self.dashboard_container.setVisible(False)
            self.btn_settings.setVisible(False)
            self.btn_riwayat.setVisible(False)
            
            # Hide menu kecuali Mode Kasir (index 0) dan Cek Stok (index 4)
            visible_indices = [0, 4]  # Mode Kasir dan Cek Stok Rendah
            for i, btn in enumerate(self.menu_buttons):
                btn.setVisible(i in visible_indices)
            
            # FIX: Kasir bisa Up dari menu ke Logout
            visible_buttons = [self.menu_buttons[i] for i in visible_indices]
            for btn in visible_buttons:
                self.register_navigation(btn, {
                    Qt.Key.Key_Up: self.btn_logout,
                    Qt.Key.Key_Return: lambda b=btn: b.click()
                })
        else:
            # Admin: Full access
            self.dashboard_container.setVisible(True)
            self.btn_settings.setVisible(True)
            self.btn_riwayat.setVisible(True)
            
            for btn in self.menu_buttons:
                btn.setVisible(True)
            
            self.refresh_dashboard()
    
    # ========== DASHBOARD ==========
    
    def lazy_load_dashboard(self):
        """Load dashboard chart"""
        if hasattr(self, 'current_role') and self.current_role == 'kasir':
            return
        
        try:
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
            from matplotlib.figure import Figure
            import matplotlib.pyplot as plt
            
            class DashboardChart(FigureCanvas):
                def __init__(self, width=5, height=3, dpi=100):
                    plt.style.use('dark_background')
                    fig = Figure(figsize=(width, height), dpi=dpi)
                    fig.patch.set_facecolor('#121212')
                    self.axes = fig.add_subplot(111)
                    super().__init__(fig)
                
                def update_chart(self, data):
                    self.axes.clear()
                    
                    if not data:
                        self.axes.text(
                            0.5, 0.5, "Belum Ada Data",
                            ha='center', va='center', color='white'
                        )
                    else:
                        tanggals = [x[0][5:] for x in data]
                        totals = [x[1] for x in data]
                        
                        bars = self.axes.bar(tanggals, totals, color='#2196F3')
                        self.axes.set_title(
                            "Penjualan 7 Hari Terakhir",
                            color='white', fontsize=10
                        )
                        
                        # Label di atas bar
                        for bar in bars:
                            yval = bar.get_height()
                            self.axes.text(
                                bar.get_x() + bar.get_width()/2, yval,
                                f"{int(yval/1000)}k",
                                ha='center', va='bottom',
                                color='white', fontsize=8
                            )
                    
                    self.draw()
            
            # Create chart
            if self.chart_layout.count() == 0:
                self.chart_view = DashboardChart(width=5, height=3)
                self.chart_layout.addWidget(self.chart_view)
            
            # Load data
            omset, trx, data_grafik = get_info_dashboard()
            self.lbl_omset_value.setText(f"Rp {int(omset):,}")
            self.lbl_trx_value.setText(str(trx))
            self.chart_view.update_chart(data_grafik)
            
        except Exception as e:
            print(f"Gagal load dashboard: {e}")
    
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        self.lazy_load_dashboard()
    
    # ========== MENU HANDLERS ==========
    
    def buka_riwayat(self):
        """Buka riwayat transaksi hari ini"""
        self.riwayat_window = RiwayatHariIniWindow()
        self.riwayat_window.set_current_user(self.current_user)
        self.riwayat_window.show()
    
    def buka_pengaturan(self):
        """Buka pengaturan toko"""
        self.pengaturan_window = PengaturanWindow()
        self.pengaturan_window.show()
    
    def buka_kasir(self):
        """Buka window kasir"""
        self.kasir_window = KasirWindow()
        self.kasir_window.set_current_user(self.current_user)
        self.kasir_window.show()
        
        # Refresh dashboard saat kasir ditutup
        def on_close(event):
            self.refresh_dashboard()
            event.accept()
        
        self.kasir_window.closeEvent = on_close
    
    def buka_produk(self):
        """Buka window produk"""
        self.produk_window = ProdukWindow()
        self.produk_window.set_current_user(self.current_user)
        self.produk_window.show()
    
    def buka_kelola_db(self):
        """Buka window kelola database"""
        self.kelola_window = KelolaDBWindow()
        self.kelola_window.set_current_user(self.current_user)
        self.kelola_window.show()
    
    def buka_laporan(self):
        """Buka window laporan"""
        self.laporan_window = LaporanWindow()
        self.laporan_window.set_current_user(self.current_user)
        self.laporan_window.show()
    
    def buka_stok_rendah(self):
        """Buka window stok rendah"""
        self.stok_rendah_window = StokRendahWindow()
        self.stok_rendah_window.set_current_user(self.current_user)
        self.stok_rendah_window.show()
    
    def buka_generate_barcode(self):
        """Buka window generate barcode"""
        self.generate_barcode_window = GenerateBarcodeWindow()
        self.generate_barcode_window.set_current_user(self.current_user)
        self.generate_barcode_window.show()
    
    def buka_manajemen_user(self):
        """Buka window manajemen user"""
        self.manajemen_user_window = ManajemenUserWindow()
        self.manajemen_user_window.set_current_user(self.current_user)
        self.manajemen_user_window.show()
    
    def buka_log_aktivitas(self):
        """Buka window log aktivitas"""
        self.log_aktivitas_window = LogAktivitasWindow()
        self.log_aktivitas_window.set_current_user(self.current_user)
        self.log_aktivitas_window.show()
    
    # ========== OVERRIDE ESC HANDLING ==========
    
    def handle_escape(self) -> bool:
        """
        Override ESC - Confirm sebelum logout
        """
        if self.confirm_action("Keluar Aplikasi", "Yakin ingin keluar dari aplikasi?"):
            if self.on_logout:
                self.on_logout()
            else:
                self.close()
            return True
        return False
    
    # ========== KEYBOARD SHORTCUTS DEFINITION ==========   
    def get_main_shortcuts(self) -> dict:
        """
        Keyboard shortcuts untuk main window
        
        Returns:
            dict: Shortcuts configuration
        """
        return {
            "Navigasi Menu": [
                ("↑↓", "Navigate menu grid (vertikal)"),
                ("←→", "Navigate menu grid (horizontal)"),
                ("Enter", "Buka menu terpilih"),
            ],
            "Header Actions": [
                ("Tab", "Pindah antar header buttons"),
                ("Enter", "Execute button"),
            ],
            "Menu Utama": [
                ("1-8", "Quick access ke menu (1=Kasir, 2=Produk, dst)"),
            ],
            "Global": [
                ("F5", "Refresh dashboard"),
                ("ESC", "Keluar aplikasi (dengan konfirmasi)"),
            ],
        }