"""
Pengaturan Window - MIGRATED TO KEYBOARD MIXIN
===============================================
✅ Clean keyboard navigation using KeyboardMixin
✅ No more eventFilter spaghetti!

BEFORE: ~50 lines of eventFilter
AFTER: ~10 lines of clean registration
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QLabel, QLineEdit, 
    QPushButton, QFormLayout, QFrame, QTextEdit
)
from PyQt6.QtCore import Qt

from src.ui.base.base_window import BaseWindow
from src.ui.base.style_manager import StyleManager
from src.settings import load_settings, save_settings


class PengaturanWindow(BaseWindow):
    """
    Window pengaturan toko
    
    ✨ MIGRATED: Clean keyboard navigation
    """
    
    def __init__(self):
        super().__init__()
        
        self.setup_ui()
        self.setup_navigation()  # ✅ Clean!
        self.muat_data()
        
        # Window properties
        self.setWindowTitle("Pengaturan Toko")
        self.setGeometry(100, 100, 600, 600)
    
    def setup_ui(self):
        """Setup UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Judul
        lbl_judul = QLabel("🔧 Konfigurasi Toko")
        lbl_judul.setStyleSheet("font-size: 20px; color: #2196F3; margin-bottom: 10px;")
        layout.addWidget(lbl_judul)
        
        # Form Container
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #181818; 
                border-radius: 10px; 
                border: 1px solid #333;
            }
        """)
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        
        # Input Fields
        self.inp_nama = QLineEdit()
        self.inp_nama.setPlaceholderText("Nama Toko")
        
        self.inp_alamat = QLineEdit()
        self.inp_alamat.setPlaceholderText("Alamat Lengkap")
        
        self.inp_telp = QLineEdit()
        self.inp_telp.setPlaceholderText("No. Telepon / HP")
        
        self.inp_footer = QTextEdit()
        self.inp_footer.setPlaceholderText("Pesan di bagian bawah struk...")
        self.inp_footer.setFixedHeight(100)
        
        # Label Style
        lbl_style = "font-weight: bold; color: #888; border: none;"
        
        form_layout.addRow(QLabel("Nama Toko:", styleSheet=lbl_style), self.inp_nama)
        form_layout.addRow(QLabel("Alamat:", styleSheet=lbl_style), self.inp_alamat)
        form_layout.addRow(QLabel("Telepon:", styleSheet=lbl_style), self.inp_telp)
        form_layout.addRow(QLabel("Footer Struk:", styleSheet=lbl_style), self.inp_footer)
        
        layout.addWidget(form_frame)
        
        # Info Navigasi
        lbl_info = QLabel("💡 Enter=Next | Tab=Next | Ctrl+S=Save | ESC=Close")
        lbl_info.setStyleSheet("color: #666; font-size: 11px; font-style: italic; margin-top: 5px;")
        layout.addWidget(lbl_info)
        
        layout.addStretch()
        
        # Tombol Simpan
        style = StyleManager()
        self.btn_simpan = QPushButton("💾 Simpan Perubahan (Ctrl+S)")
        self.btn_simpan.setStyleSheet(style.get_button_style('success'))
        self.btn_simpan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_simpan.clicked.connect(self.simpan_data)
        layout.addWidget(self.btn_simpan)
        
        # Focus awal
        self.inp_nama.setFocus()
    
    def setup_navigation(self):
        """
        ✨ CLEAN NAVIGATION SETUP
        
        BEFORE: 50+ lines of eventFilter with Tab/Enter handling
        AFTER: Just 10 lines! 🎉
        """
        
        # ===== FORM NAVIGATION =====
        # Nama: Enter/Down = Alamat
        self.register_navigation(self.inp_nama, {
            Qt.Key.Key_Return: self.inp_alamat,
            Qt.Key.Key_Down: self.inp_alamat
        })
        
        # Alamat: Enter/Down = Telepon, Up = Nama
        self.register_navigation(self.inp_alamat, {
            Qt.Key.Key_Return: self.inp_telp,
            Qt.Key.Key_Down: self.inp_telp,
            Qt.Key.Key_Up: self.inp_nama
        })
        
        # Telepon: Enter/Down = Footer, Up = Alamat
        self.register_navigation(self.inp_telp, {
            Qt.Key.Key_Return: self.inp_footer,
            Qt.Key.Key_Down: self.inp_footer,
            Qt.Key.Key_Up: self.inp_alamat
        })
        
        # Footer: Tab = Tombol Simpan, Up = Telepon
        # Note: Enter tidak karena untuk new line di TextEdit
        self.register_navigation(self.inp_footer, {
            Qt.Key.Key_Up: self.inp_telp  # Ctrl+Up handled by base
        })
        
        # Tombol: Enter = Simpan, Up = Footer
        self.register_navigation(self.btn_simpan, {
            Qt.Key.Key_Return: self.simpan_data,
            Qt.Key.Key_Up: self.inp_footer
        })
        
        # ===== GLOBAL SHORTCUTS =====
        # Ctrl+S = Save (already handled by KeyboardMixin!)
        # ESC = Close (already handled by KeyboardMixin!)
        
        # Custom: Tab untuk footer → button
        self.register_shortcut(Qt.Key.Key_Tab, 
                              lambda: self.btn_simpan.setFocus() if self.inp_footer.hasFocus() else None)
    
    # ========== NO MORE EVENTFILTER! ==========
    # ✅ All handled by KeyboardMixin!
    
    def muat_data(self):
        """Load settings dari file"""
        data = load_settings()
        self.inp_nama.setText(data.get("nama_toko", ""))
        self.inp_alamat.setText(data.get("alamat_toko", ""))
        self.inp_telp.setText(data.get("telepon", ""))
        self.inp_footer.setText(data.get("footer_struk", ""))
    
    def simpan_data(self):
        """Simpan settings (Ctrl+S)"""
        data = {
            "nama_toko": self.inp_nama.text().strip(),
            "alamat_toko": self.inp_alamat.text().strip(),
            "telepon": self.inp_telp.text().strip(),
            "footer_struk": self.inp_footer.toPlainText().strip()
        }
        
        # Validasi
        if not data["nama_toko"]:
            self.show_warning("Error", "Nama Toko wajib diisi!")
            self.inp_nama.setFocus()
            return
        
        try:
            save_settings(data)
            self.show_success("Sukses", "Pengaturan berhasil disimpan!")
            self.close()
        except Exception as e:
            self.show_error("Error", f"Gagal menyimpan: {e}")