from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton, QGridLayout, QLabel,
    QSizePolicy, QHBoxLayout, QFrame
)
from PyQt6.QtCore import QSize, Qt, QEvent, QTimer
from src.ui.kasir_window import KasirWindow
from src.ui.produk_window import ProdukWindow
from src.ui.kelola_db_window import KelolaDBWindow
from src.ui.laporan_window import LaporanWindow
from src.ui.stok_rendah_window import StokRendahWindow
from src.ui.generate_barcode_window import GenerateBarcodeWindow
from src.ui.manajemen_user_window import ManajemenUserWindow
from src.ui.log_aktivitas_window import LogAktivitasWindow
from src.database import get_info_dashboard

class MainWindow(QMainWindow):
    def __init__(self, on_logout=None):
        super().__init__()
        self.setWindowTitle("Sistem Kasir Pro")
        self.setGeometry(100, 100, 1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background-color: #121212;") 

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # 1. HEADER
        header_layout = QHBoxLayout()
        self.lbl_judul = QLabel("Dashboard")
        self.lbl_judul.setStyleSheet("color: #ffffff; font-size: 24px; font-weight: bold;")
        
        # --- TOMBOL LOGOUT (HEADER) ---
        self.btn_logout = QPushButton("Logout")
        self.btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_logout.setFixedSize(100, 40)
        self.btn_logout.setStyleSheet("""
            QPushButton { background-color: #d32f2f; color: white; border-radius: 5px; font-weight: bold; }
            QPushButton:focus { border: 2px solid #ff5252; }
        """)
        
        if on_logout:
            self.btn_logout.clicked.connect(on_logout)
        else:
            self.btn_logout.clicked.connect(self.close)
            
        self.btn_logout.setAutoDefault(True)
        self.btn_logout.installEventFilter(self)
        self.btn_logout.setProperty("is_logout", True)

        header_layout.addWidget(self.lbl_judul)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_logout) # Logout masuk di Header (Atas)
        main_layout.addLayout(header_layout)

        # 2. DASHBOARD AREA
        self.dashboard_container = QWidget()
        self.dash_layout = QHBoxLayout(self.dashboard_container)
        self.dash_layout.setContentsMargins(0, 10, 0, 10)
        
        info_panel = QVBoxLayout()
        self.card_omset = QFrame()
        self.card_omset.setStyleSheet("background-color: #1E1E1E; border-radius: 10px; border: 1px solid #333;")
        card1_layout = QVBoxLayout(self.card_omset)
        self.lbl_omset_title = QLabel("Omset Hari Ini")
        self.lbl_omset_title.setStyleSheet("color: #aaa; font-size: 14px;")
        self.lbl_omset_value = QLabel("Loading...") 
        self.lbl_omset_value.setStyleSheet("color: #4CAF50; font-size: 28px; font-weight: bold;")
        card1_layout.addWidget(self.lbl_omset_title)
        card1_layout.addWidget(self.lbl_omset_value)
        
        self.card_trx = QFrame()
        self.card_trx.setStyleSheet("background-color: #1E1E1E; border-radius: 10px; border: 1px solid #333;")
        card2_layout = QVBoxLayout(self.card_trx)
        self.lbl_trx_title = QLabel("Total Transaksi")
        self.lbl_trx_title.setStyleSheet("color: #aaa; font-size: 14px;")
        self.lbl_trx_value = QLabel("-")
        self.lbl_trx_value.setStyleSheet("color: #2196F3; font-size: 28px; font-weight: bold;")
        card2_layout.addWidget(self.lbl_trx_title)
        card2_layout.addWidget(self.lbl_trx_value)
        
        info_panel.addWidget(self.card_omset)
        info_panel.addWidget(self.card_trx)
        
        self.chart_container = QWidget() 
        self.chart_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.chart_layout = QVBoxLayout(self.chart_container) 
        
        self.dash_layout.addLayout(info_panel, 1)
        self.dash_layout.addWidget(self.chart_container, 2)
        
        main_layout.addWidget(self.dashboard_container)

        # 3. MENU GRID
        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
        grid_layout.setSpacing(15) 
        
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
                background-color: #1E1E1E; color: #E0E0E0; font-size: 14px; font-weight: bold;
                border: 2px solid #333333; border-radius: 10px; padding: 10px; outline: none;
            }
            QPushButton:hover { background-color: #2D2D2D; border: 2px solid #555555; }
            QPushButton:focus { background-color: #252525; border: 2px solid #2196F3; color: #ffffff; }
        """

        self.buttons = []
        row = 0; col = 0; self.max_col = 4 

        for i, (text, handler) in enumerate(buttons_config):
            btn = QPushButton(text)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.setMinimumHeight(80)
            btn.setStyleSheet(btn_style)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            btn.setAutoDefault(True); btn.setDefault(False)
            btn.installEventFilter(self)
            btn.setProperty("index", i)
            btn.clicked.connect(handler)
            
            grid_layout.addWidget(btn, row, col)
            self.buttons.append(btn)

            col += 1
            if col >= self.max_col: col = 0; row += 1

        main_layout.addWidget(grid_container)
        
        # [PENTING] Variabel Ingatan Navigasi
        self.last_focused_index = 0 

        QTimer.singleShot(100, self.lazy_load_dashboard)

        if self.buttons: self.buttons[0].setFocus()

    def set_user_role(self, username, role):
        self.current_user = username
        self.current_role = role
        role_disp = "ADMINISTRATOR" if role == "admin" else "KASIR"
        self.lbl_judul.setText(f"Dashboard - {username} ({role_disp})")

        if role == "kasir":
            self.dashboard_container.setVisible(False)
            tombol_dilarang = [1, 2, 3, 5, 6, 7]
            for index in tombol_dilarang:
                self.buttons[index].setVisible(False)
        else:
            self.dashboard_container.setVisible(True)
            for btn in self.buttons:
                btn.setVisible(True)
            # Data akan di-refresh oleh lazy_load_dashboard

    def lazy_load_dashboard(self):
        if hasattr(self, 'current_role') and self.current_role == 'kasir': return

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
                        self.axes.text(0.5, 0.5, "Belum Ada Data", ha='center', va='center', color='white')
                    else:
                        tanggals = [x[0][5:] for x in data]
                        totals = [x[1] for x in data]
                        bars = self.axes.bar(tanggals, totals, color='#2196F3')
                        self.axes.set_title("Penjualan 7 Hari Terakhir", color='white', fontsize=10)
                        for bar in bars:
                            yval = bar.get_height()
                            self.axes.text(bar.get_x() + bar.get_width()/2, yval, f"{int(yval/1000)}k", ha='center', va='bottom', color='white', fontsize=8)
                    self.draw()

            if self.chart_layout.count() == 0:
                self.chart_view = DashboardChart(width=5, height=3)
                self.chart_layout.addWidget(self.chart_view)
            
            omset, trx, data_grafik = get_info_dashboard()
            self.lbl_omset_value.setText(f"Rp {int(omset):,}")
            self.lbl_trx_value.setText(str(trx))
            self.chart_view.update_chart(data_grafik)

        except Exception as e:
            print(f"Gagal load dashboard: {e}")

    def refresh_dashboard(self):
        self.lazy_load_dashboard()

    # --- NAVIGASI KEYBOARD PINTAR (DENGAN INGATAN) ---
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            
            current_index = obj.property("index")
            is_logout = obj.property("is_logout")

            # --- SKENARIO A: SEDANG DI TOMBOL GRID ---
            if current_index is not None:
                # [BARU] Simpan posisi ini ke ingatan
                self.last_focused_index = current_index
                
                next_index = None
                
                # 1. KANAN
                if event.key() == Qt.Key.Key_Right:
                    if (current_index + 1) < len(self.buttons): 
                        if self.buttons[current_index + 1].isVisible(): next_index = current_index + 1
                
                # 2. KIRI
                elif event.key() == Qt.Key.Key_Left:
                    if (current_index - 1) >= 0:
                        if self.buttons[current_index - 1].isVisible(): next_index = current_index - 1
                
                # 3. BAWAH
                elif event.key() == Qt.Key.Key_Down:
                    target = current_index + 4
                    if current_index >= 4 or (target < len(self.buttons) and not self.buttons[target].isVisible()): 
                        self.btn_logout.setFocus(); return True
                    elif target < len(self.buttons): next_index = target
                
                # 4. ATAS
                elif event.key() == Qt.Key.Key_Up:
                    target = current_index - 4
                    if target >= 0 and self.buttons[target].isVisible(): next_index = target
                    elif target < 0: 
                        self.btn_logout.setFocus(); return True # Loncat ke Logout
                
                # 5. ENTER
                elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    obj.click(); return True

                if next_index is not None: 
                    self.buttons[next_index].setFocus()
                    return True

            # --- SKENARIO B: SEDANG DI TOMBOL LOGOUT ---
            elif is_logout:
                # [PERBAIKAN] Tekan BAWAH -> Kembali ke tombol terakhir yang diingat
                if event.key() == Qt.Key.Key_Down:
                    # Cek apakah tombol terakhir masih terlihat (misal habis ganti role)?
                    if self.buttons[self.last_focused_index].isVisible():
                        self.buttons[self.last_focused_index].setFocus()
                        return True
                    else:
                        # Kalau tombol ingatan hilang, cari tombol visible pertama dari awal
                        for i in range(len(self.buttons)):
                            if self.buttons[i].isVisible():
                                self.buttons[i].setFocus()
                                return True
                
                # ENTER
                elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    obj.click(); return True

        return super().eventFilter(obj, event)

    # --- HANDLERS ---
    def buka_kasir(self):
        self.kasir_window = KasirWindow()
        self.kasir_window.set_current_user(self.current_user)
        self.kasir_window.show()
        self.kasir_window.closeEvent = lambda event: self.refresh_dashboard()

    def buka_produk(self):
        self.produk_window = ProdukWindow()
        self.produk_window.set_current_user(self.current_user)
        self.produk_window.show()

    def buka_kelola_db(self):
        self.kelola_window = KelolaDBWindow()
        self.kelola_window.set_current_user(self.current_user)
        self.kelola_window.show()

    def buka_laporan(self):
        self.laporan_window = LaporanWindow()
        self.laporan_window.set_current_user(self.current_user)
        self.laporan_window.show()

    def buka_stok_rendah(self):
        self.stok_rendah_window = StokRendahWindow()
        self.stok_rendah_window.set_current_user(self.current_user)
        self.stok_rendah_window.show()

    def buka_generate_barcode(self):
        self.generate_barcode_window = GenerateBarcodeWindow()
        self.generate_barcode_window.set_current_user(self.current_user)
        self.generate_barcode_window.show()

    def buka_manajemen_user(self):
        self.manajemen_user_window = ManajemenUserWindow()
        self.manajemen_user_window.set_current_user(self.current_user)
        self.manajemen_user_window.show()

    def buka_log_aktivitas(self):
        self.log_aktivitas_window = LogAktivitasWindow()
        self.log_aktivitas_window.set_current_user(self.current_user)
        self.log_aktivitas_window.show()