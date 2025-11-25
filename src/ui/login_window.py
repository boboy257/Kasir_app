from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QHBoxLayout,
    QLineEdit, QLabel, QPushButton, QMessageBox,
    QFormLayout
)
from PyQt6.QtCore import Qt
from src.database import cek_login

class LoginWindow(QMainWindow):
    def __init__(self, on_login_success=None):
        super().__init__()
        self.setWindowTitle("Login - Aplikasi Kasir")
        self.setGeometry(100, 100, 400, 200)
        self.setFixedSize(400, 200)  # Jendela tidak bisa di-resize

        # Simpan fungsi callback untuk dipanggil saat login sukses
        self.on_login_success = on_login_success

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Form login
        form_layout = QFormLayout()

        # Input username
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Masukkan username")
        form_layout.addRow("Username:", self.input_username)

        # Input password
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)  # Sembunyikan karakter
        self.input_password.setPlaceholderText("Masukkan password")
        form_layout.addRow("Password:", self.input_password)

        layout.addLayout(form_layout)

        # Tombol login
        self.btn_login = QPushButton("Login")
        self.btn_login.clicked.connect(self.login)
        layout.addWidget(self.btn_login)

        # Fokus ke input username saat pertama kali dibuka
        self.input_username.setFocus()

        # Aktifkan tombol login saat tekan Enter di password
        self.input_password.returnPressed.connect(self.login)

    def login(self):
        """Fungsi untuk memproses login"""
        username = self.input_username.text().strip()
        password = self.input_password.text().strip()

        # Validasi input tidak kosong
        if not username or not password:
            QMessageBox.warning(self, "Input Tidak Lengkap", "Username dan password harus diisi.")
            return

        # Cek login di database
        if cek_login(username, password):
            # Jika login berhasil
            QMessageBox.information(self, "Login Berhasil", f"Selamat datang, {username}!")
            
            # Panggil callback jika login sukses
            if self.on_login_success:
                self.on_login_success()
            
            # Tutup jendela login
            self.close()
        else:
            # Jika login gagal
            QMessageBox.critical(self, "Login Gagal", "Username atau password salah.")
            # Kosongkan input password
            self.input_password.clear()
            # Fokus kembali ke input username
            self.input_username.setFocus()