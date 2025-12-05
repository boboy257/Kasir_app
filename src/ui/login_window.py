from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QHBoxLayout,
    QLineEdit, QLabel, QPushButton, QMessageBox,
    QFormLayout, QFrame
)
from PyQt6.QtCore import Qt, QEvent
from src.database import cek_login

class LoginWindow(QMainWindow):
    def __init__(self, on_login_success=None):
        super().__init__()
        self.setWindowTitle("Login - Aplikasi Kasir")
        self.setGeometry(100, 100, 450, 300)
        self.setFixedSize(450, 320) # Ukuran pas

        self.on_login_success = on_login_success

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # --- STYLING DARK MODE ---
        self.setStyleSheet("""
            QWidget { 
                background-color: #121212; 
                color: #e0e0e0; 
                font-family: 'Segoe UI', sans-serif; 
                font-size: 14px;
                outline: none;
            }
            
            QLineEdit { 
                background-color: #1E1E1E; 
                border: 1px solid #333; 
                padding: 12px; 
                color: white; 
                border-radius: 5px;
            }
            QLineEdit:focus { 
                border: 2px solid #2196F3; /* Border Biru saat fokus */
                background-color: #252525;
            }
            
            QPushButton { 
                background-color: #2196F3; 
                color: white; 
                border: none; 
                padding: 12px; 
                border-radius: 5px; 
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover { background-color: #1976D2; }
            QPushButton:focus { 
                border: 3px solid #ffffff; /* Fokus Putih Jelas */
            }
            
            QLabel { font-weight: bold; color: #bbb; }
        """)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Judul
        lbl_judul = QLabel("🔐 Log in")
        lbl_judul.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_judul.setStyleSheet("font-size: 22px; color: #fff; margin-bottom: 10px;")
        layout.addWidget(lbl_judul)

        # Form Input
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Username")
        self.input_username.installEventFilter(self) # Pasang Telinga

        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setPlaceholderText("Password")
        self.input_password.installEventFilter(self)

        layout.addWidget(self.input_username)
        layout.addWidget(self.input_password)
        
        layout.addSpacing(10)

        # Tombol Login
        self.btn_login = QPushButton("LOG IN")
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.clicked.connect(self.login)
        self.btn_login.installEventFilter(self)
        
        layout.addWidget(self.btn_login)
        layout.addStretch()

        # Fokus Awal
        self.input_username.setFocus()
        
        # [PENTING] Install Event Filter di Window
        self.installEventFilter(self)

    # --- LOGIKA NAVIGASI KEYBOARD ---
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            
            # GLOBAL: ESC -> Tutup Aplikasi
            if event.key() == Qt.Key.Key_Escape:
                self.close()
                return True

            # 1. USERNAME
            if obj == self.input_username:
                # Enter / Panah Bawah -> Password
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Down):
                    self.input_password.setFocus()
                    self.input_password.selectAll()
                    return True
            
            # 2. PASSWORD
            elif obj == self.input_password:
                # Enter -> LOGIN
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self.login()
                    return True
                # Bawah -> Tombol Login
                elif event.key() == Qt.Key.Key_Down:
                    self.btn_login.setFocus()
                    return True
                # Atas -> Username
                elif event.key() == Qt.Key.Key_Up:
                    self.input_username.setFocus()
                    self.input_username.selectAll()
                    return True

            # 3. TOMBOL LOGIN
            elif obj == self.btn_login:
                # Enter -> LOGIN
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self.login()
                    return True
                # Atas -> Password
                elif event.key() == Qt.Key.Key_Up:
                    self.input_password.setFocus()
                    self.input_password.selectAll()
                    return True

        return super().eventFilter(obj, event)

    def login(self):
        username = self.input_username.text().strip()
        password = self.input_password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Input Tidak Lengkap", "Username dan password harus diisi.")
            self.input_username.setFocus()
            return

        # Cek Login Database
        role = cek_login(username, password)
        
        if role:
            # Login Berhasil
            if self.on_login_success:
                self.on_login_success(username, role)
            self.close()
        else:
            QMessageBox.critical(self, "Login Gagal", "Username atau password salah.")
            self.input_password.clear()
            self.input_password.setFocus() # Fokus balik ke password biar bisa ketik ulang cepat