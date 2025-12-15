"""
Login Window - REFACTORED VERSION
==================================
Menggunakan BaseWindow untuk konsistensi
"""

from PyQt6.QtWidgets import QVBoxLayout, QWidget, QLineEdit, QLabel, QPushButton
from PyQt6.QtCore import Qt
from src.ui.base.base_window import BaseWindow
from src.ui.base.style_manager import StyleManager
from src.database import cek_login

class LoginWindow(BaseWindow):
    """
    Login window dengan keyboard navigation
    
    Features:
    - Simple keyboard navigation (Enter = next field)
    - ESC = close
    - Pakai BaseWindow untuk konsistensi
    """
    
    def __init__(self, on_login_success=None):
        super().__init__()
        
        self.on_login_success = on_login_success
        
        # Setup UI
        self.setup_ui()
        self.setup_navigation()
        
        # Window properties
        self.setWindowTitle("Login - Aplikasi Kasir")
        self.setGeometry(100, 100, 450, 320)
        self.setFixedSize(450, 320)
    
    def setup_ui(self):
        """Setup UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Judul
        lbl_judul = QLabel("🔐 Log in")
        lbl_judul.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_judul.setStyleSheet("font-size: 22px; color: #fff; margin-bottom: 10px;")
        layout.addWidget(lbl_judul)
        
        # Input Username
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Username")
        layout.addWidget(self.input_username)
        
        # Input Password
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setPlaceholderText("Password")
        layout.addWidget(self.input_password)
        
        layout.addSpacing(10)
        
        # Tombol Login
        style = StyleManager()
        self.btn_login = QPushButton("LOG IN")
        self.btn_login.setStyleSheet(style.get_button_style('primary'))
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.clicked.connect(self.login)
        layout.addWidget(self.btn_login)
        
        layout.addStretch()
        
        # Fokus awal
        self.input_username.setFocus()
    
    def setup_navigation(self):
        """
        Setup keyboard navigation
        
        JAUH LEBIH SIMPLE dari versi lama! 🎉
        """
        # Username: Enter/Down = pindah ke password
        self.register_navigation(self.input_username, {
            Qt.Key.Key_Down: self.input_password,
            Qt.Key.Key_Return: self.input_password
        })
        
        # Password: Enter = login, Up = balik ke username, Down = tombol
        self.register_navigation(self.input_password, {
            Qt.Key.Key_Return: self.login,
            Qt.Key.Key_Up: self.input_username,
            Qt.Key.Key_Down: self.btn_login
        })
        
        # Tombol: Enter = login, Up = balik ke password
        self.register_navigation(self.btn_login, {
            Qt.Key.Key_Return: self.login,
            Qt.Key.Key_Up: self.input_password
        })
    
    def login(self):
        """Handle login logic"""
        username = self.input_username.text().strip()
        password = self.input_password.text().strip()
        
        # Validasi input
        if not username or not password:
            self.show_warning("Input Tidak Lengkap", "Username dan password harus diisi.")
            self.input_username.setFocus()
            return
        
        # Cek login ke database
        role = cek_login(username, password)
        
        if role:
            # Login berhasil
            if self.on_login_success:
                self.on_login_success(username, role)
            self.close()
        else:
            # Login gagal
            self.show_error("Login Gagal", "Username atau password salah.")
            self.input_password.clear()
            self.input_password.setFocus()