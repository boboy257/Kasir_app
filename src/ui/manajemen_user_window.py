from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QHBoxLayout,
    QLineEdit, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QFormLayout, QDialog
)
from src.database import (
    semua_user, tambah_user_baru, update_user, hapus_user, cek_username_sudah_ada
)

class ManajemenUserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manajemen Pengguna")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Form input user
        form_layout = QFormLayout()
        
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Masukkan username")
        form_layout.addRow("Username:", self.input_username)
        
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setPlaceholderText("Masukkan password")
        form_layout.addRow("Password:", self.input_password)
        
        layout.addLayout(form_layout)

        # Tombol aksi
        btn_layout = QHBoxLayout()
        
        self.btn_simpan = QPushButton("Simpan User")
        self.btn_simpan.clicked.connect(self.simpan_user)
        
        self.btn_batal = QPushButton("Batal")
        self.btn_batal.clicked.connect(self.bersihkan_form)
        
        btn_layout.addWidget(self.btn_simpan)
        btn_layout.addWidget(self.btn_batal)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)

        # Tabel user
        self.table_user = QTableWidget(0, 3)
        self.table_user.setHorizontalHeaderLabels(["ID", "Username", "Aksi"])
        layout.addWidget(QLabel("Daftar Pengguna:"))
        layout.addWidget(self.table_user)

        # Muat data user
        self.muat_user()

    def muat_user(self):
        """Muat semua user ke tabel"""
        self.table_user.setRowCount(0)
        user_list = semua_user()
        
        for row, (id_user, username) in enumerate(user_list):
            self.table_user.insertRow(row)
            self.table_user.setItem(row, 0, QTableWidgetItem(str(id_user)))
            self.table_user.setItem(row, 1, QTableWidgetItem(username))
            
            # Kolom Aksi: Edit dan Hapus
            aksi_widget = QWidget()
            aksi_layout = QHBoxLayout(aksi_widget)
            aksi_layout.setContentsMargins(5, 2, 5, 2)
            aksi_layout.setSpacing(2)
            
            btn_edit = QPushButton("Edit")
            btn_edit.clicked.connect(lambda checked, id=id_user: self.edit_user(id))
            
            btn_hapus = QPushButton("Hapus")
            btn_hapus.clicked.connect(lambda checked, id=id_user: self.hapus_user(id))
            
            aksi_layout.addWidget(btn_edit)
            aksi_layout.addWidget(btn_hapus)
            aksi_layout.addStretch()
            
            self.table_user.setCellWidget(row, 2, aksi_widget)

    def simpan_user(self):
        """Simpan atau update user"""
        username = self.input_username.text().strip()
        password = self.input_password.text().strip()
        
        if not username:
            QMessageBox.warning(self, "Input Tidak Lengkap", "Username harus diisi.")
            return
        
        if not hasattr(self, 'user_yang_diedit'):
            # Mode tambah user baru
            if cek_username_sudah_ada(username):
                QMessageBox.warning(self, "Username Sudah Ada", f"Username '{username}' sudah digunakan.")
                return
            
            if not password:
                QMessageBox.warning(self, "Input Tidak Lengkap", "Password harus diisi untuk user baru.")
                return
            
            if tambah_user_baru(username, password):
                QMessageBox.information(self, "Berhasil", "User baru berhasil ditambahkan.")
                self.bersihkan_form()
                self.muat_user()
            else:
                QMessageBox.critical(self, "Gagal", "Gagal menambah user baru.")
        else:
            # Mode update user
            if cek_username_sudah_ada(username, self.user_yang_diedit):
                QMessageBox.warning(self, "Username Sudah Ada", f"Username '{username}' sudah digunakan user lain.")
                return
            
            update_user(self.user_yang_diedit, username, password if password else None)
            QMessageBox.information(self, "Berhasil", "User berhasil diupdate.")
            self.bersihkan_form()
            self.muat_user()

    def edit_user(self, id_user):
        """Edit user berdasarkan ID"""
        user_list = semua_user()
        user = None
        for id_db, username in user_list:
            if id_db == id_user:
                user = (id_db, username)
                break
        
        if user:
            id_user, username = user
            self.input_username.setText(username)
            self.input_password.clear()
            self.input_password.setPlaceholderText("Kosongkan jika tidak ingin ganti password")
            self.btn_simpan.setText("Update User")
            self.user_yang_diedit = id_user

    def hapus_user(self, id_user):
        """Hapus user berdasarkan ID"""
        reply = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            "Apakah Anda yakin ingin menghapus user ini?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            hapus_user(id_user)
            QMessageBox.information(self, "Berhasil", "User berhasil dihapus.")
            self.muat_user()

    def bersihkan_form(self):
        """Bersihkan form input"""
        self.input_username.clear()
        self.input_password.clear()
        self.btn_simpan.setText("Simpan User")
        if hasattr(self, 'user_yang_diedit'):
            del self.user_yang_diedit

    def set_current_user(self, username):
        """Set username untuk window ini"""
        self.current_user = username