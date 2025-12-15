"""
Manajemen User Window - REFACTORED VERSION
===========================================
Menggunakan BaseWindow untuk konsistensi
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QFormLayout, 
    QComboBox, QHeaderView, QAbstractItemView, QFrame
)
from PyQt6.QtCore import Qt, QEvent

from src.ui.base.base_window import BaseWindow
from src.ui.base.style_manager import StyleManager
from src.database import (
    semua_user, tambah_user_baru, update_user, 
    hapus_user, cek_username_sudah_ada
)

class ManajemenUserWindow(BaseWindow):
    """
    Window untuk manajemen user (CRUD)
    
    Features:
    - Tambah user baru
    - Edit user existing
    - Hapus user
    - Role management (admin/kasir)
    """
    
    def __init__(self):
        super().__init__()
        
        self.user_yang_diedit = None
        
        self.setup_ui()
        self.setup_navigation()
        
        # Window properties
        self.setWindowTitle("Manajemen Pengguna (Admin Only)")
        self.setGeometry(100, 100, 950, 550)
        
        # Load data
        self.muat_user()
    
    def setup_ui(self):
        """Setup UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # ===== LEFT SIDE: FORM =====
        form_container = QFrame()
        form_container.setFixedWidth(320)
        form_container.setStyleSheet(
            "background-color: #181818; border-radius: 10px; border: 1px solid #333;"
        )
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_judul = QLabel("📝 Form Pengguna")
        lbl_judul.setStyleSheet(
            "font-size: 18px; color: #29b6f6; border: none; background: transparent;"
        )
        form_layout.addWidget(lbl_judul)
        
        # Form inputs
        input_group = QFormLayout()
        input_group.setVerticalSpacing(15)
        
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Masukkan username")
        
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setPlaceholderText("Isi password...")
        
        self.combo_role = QComboBox()
        self.combo_role.addItem("Kasir", "kasir")
        self.combo_role.addItem("Administrator", "admin")
        self.combo_role.setCursor(Qt.CursorShape.PointingHandCursor)
        
        lbl_style = "font-weight: bold; color: #bbb; border: none; background: transparent;"
        input_group.addRow(QLabel("Username:", styleSheet=lbl_style), self.input_username)
        input_group.addRow(QLabel("Password:", styleSheet=lbl_style), self.input_password)
        input_group.addRow(QLabel("Role:", styleSheet=lbl_style), self.combo_role)
        
        form_layout.addLayout(input_group)
        form_layout.addSpacing(25)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        style = StyleManager()
        
        self.btn_simpan = QPushButton("Simpan Data")
        self.btn_simpan.setStyleSheet(style.get_button_style('success'))
        self.btn_simpan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_simpan.clicked.connect(self.simpan_user)
        
        self.btn_batal = QPushButton("Reset")
        self.btn_batal.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_batal.clicked.connect(self.bersihkan_form)
        
        btn_layout.addWidget(self.btn_simpan)
        btn_layout.addWidget(self.btn_batal)
        form_layout.addLayout(btn_layout)
        
        form_layout.addStretch()
        
        lbl_nav = QLabel("Navigasi: Enter & Panah | F2: Edit | Del: Hapus")
        lbl_nav.setStyleSheet(
            "color:#777; font-size:11px; background:transparent; border:none;"
        )
        form_layout.addWidget(lbl_nav)
        
        layout.addWidget(form_container)
        
        # ===== RIGHT SIDE: TABLE =====
        table_container = QVBoxLayout()
        
        lbl_tabel = QLabel("Daftar Pengguna Sistem:")
        lbl_tabel.setStyleSheet(
            "font-size: 14px; font-weight: bold; margin-bottom: 5px; color: #ddd;"
        )
        table_container.addWidget(lbl_tabel)
        
        self.table_user = QTableWidget(0, 4)
        self.table_user.setHorizontalHeaderLabels(["ID", "Username", "Role", "Aksi"])
        self.table_user.setColumnHidden(0, True)
        self.table_user.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_user.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_user.verticalHeader().setVisible(False)
        self.table_user.setShowGrid(False)
        self.table_user.setAlternatingRowColors(True)
        self.table_user.setStyleSheet(
            "QTableWidget { alternate-background-color: #252525; background-color: #1E1E1E; }"
        )
        
        header = self.table_user.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        table_container.addWidget(self.table_user)
        layout.addLayout(table_container)
        
        # Focus awal
        self.input_username.setFocus()
    
    def setup_navigation(self):
        """Setup keyboard navigation"""
        
        # Username
        self.register_navigation(self.input_username, {
            Qt.Key.Key_Down: self.input_password,
            Qt.Key.Key_Return: self.input_password
        })
        
        # Password
        self.register_navigation(self.input_password, {
            Qt.Key.Key_Up: self.input_username,
            Qt.Key.Key_Down: self.combo_role,
            Qt.Key.Key_Return: lambda: (self.combo_role.setFocus(), self.combo_role.showPopup())
        })
        
        # Role Combo
        self.register_navigation(self.combo_role, {
            Qt.Key.Key_Up: self.input_password,
            Qt.Key.Key_Down: self.btn_simpan,
            Qt.Key.Key_Return: self.btn_simpan
        })
        
        # Button Simpan
        self.register_navigation(self.btn_simpan, {
            Qt.Key.Key_Up: self.combo_role,
            Qt.Key.Key_Right: self.btn_batal,
            Qt.Key.Key_Down: lambda: self.focus_table_first_row(self.table_user),
            Qt.Key.Key_Return: self.simpan_user
        })
        
        # Button Batal
        self.register_navigation(self.btn_batal, {
            Qt.Key.Key_Up: self.combo_role,
            Qt.Key.Key_Left: self.btn_simpan,
            Qt.Key.Key_Down: lambda: self.focus_table_first_row(self.table_user),
            Qt.Key.Key_Return: self.bersihkan_form
        })
    
    def eventFilter(self, obj, event):
        """Handle special keys untuk table"""
        if event.type() == QEvent.Type.KeyPress:
            
            # Ctrl+Down: Jump to table
            if (event.modifiers() == Qt.KeyboardModifier.ControlModifier and 
                event.key() == Qt.Key.Key_Down):
                if self.table_user.rowCount() > 0:
                    self.focus_table_first_row(self.table_user)
                return True
            
            # Ctrl+Up: Back to form
            if (event.modifiers() == Qt.KeyboardModifier.ControlModifier and 
                event.key() == Qt.Key.Key_Up):
                self.input_username.setFocus()
                return True
            
            # Table shortcuts
            if obj == self.table_user:
                # Up di baris 0 = balik ke form
                if event.key() == Qt.Key.Key_Up and self.table_user.currentRow() == 0:
                    self.btn_simpan.setFocus()
                    return True
                
                # F2 = Edit
                if event.key() == Qt.Key.Key_F2:
                    self.edit_current_row()
                    return True
                
                # Delete = Hapus
                if event.key() == Qt.Key.Key_Delete:
                    self.delete_current_row()
                    return True
        
        return super().eventFilter(obj, event)
    
    # ========== TABLE SHORTCUTS ==========
    
    def edit_current_row(self):
        """Edit user dari baris yang dipilih"""
        row = self.table_user.currentRow()
        if row >= 0:
            user_id = self.table_user.item(row, 0).text()
            self.edit_user(user_id)
    
    def delete_current_row(self):
        """Hapus user dari baris yang dipilih"""
        row = self.table_user.currentRow()
        if row >= 0:
            user_id = self.table_user.item(row, 0).text()
            self.hapus_user(user_id)
    
    # ========== DATA OPERATIONS ==========
    
    def muat_user(self):
        """Load semua user ke table"""
        self.table_user.setRowCount(0)
        user_list = semua_user()
        
        for row, (id_user, username, role) in enumerate(user_list):
            self.table_user.insertRow(row)
            self.table_user.setItem(row, 0, QTableWidgetItem(str(id_user)))
            self.table_user.setItem(row, 1, QTableWidgetItem(username))
            
            role_item = QTableWidgetItem(role.upper())
            role_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if role == 'admin':
                role_item.setForeground(Qt.GlobalColor.cyan)
            else:
                role_item.setForeground(Qt.GlobalColor.yellow)
            
            self.table_user.setItem(row, 2, role_item)
            
            # Action buttons
            btn_container = QWidget()
            btn_container.setStyleSheet("background: transparent; border: none;")
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            btn_layout.setSpacing(5)
            
            btn_edit = QPushButton("Edit")
            btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_edit.setStyleSheet(
                "QPushButton { background-color: #FF9800; color: white; "
                "border: none; border-radius: 3px; padding: 5px; } "
                "QPushButton:focus { border: 2px solid #FFF; }"
            )
            btn_edit.clicked.connect(lambda checked, uid=id_user: self.edit_user(uid))
            
            btn_hapus = QPushButton("Hapus")
            btn_hapus.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_hapus.setStyleSheet(
                "QPushButton { background-color: #f44336; color: white; "
                "border: none; border-radius: 3px; padding: 5px; } "
                "QPushButton:focus { border: 2px solid #FFF; }"
            )
            btn_hapus.clicked.connect(lambda checked, uid=id_user: self.hapus_user(uid))
            
            btn_layout.addWidget(btn_edit)
            btn_layout.addWidget(btn_hapus)
            self.table_user.setCellWidget(row, 3, btn_container)
    
    def simpan_user(self):
        """Simpan user baru atau update existing"""
        username = self.input_username.text().strip()
        password = self.input_password.text().strip()
        role = self.combo_role.currentData()
        
        # Validasi
        if not username:
            self.show_warning("Input", "Username harus diisi.")
            self.input_username.setFocus()
            return
        
        # Mode tambah baru
        if self.user_yang_diedit is None:
            if not password:
                self.show_warning("Input", "Password wajib diisi.")
                self.input_password.setFocus()
                return
            
            if cek_username_sudah_ada(username):
                self.show_warning("Gagal", "Username sudah dipakai.")
                self.input_username.setFocus()
                return
            
            if tambah_user_baru(username, password, role):
                self.show_success("Berhasil", "User berhasil ditambahkan.")
                self.bersihkan_form()
                self.muat_user()
            else:
                self.show_error("Error", "Gagal menyimpan user.")
        
        # Mode update
        else:
            if cek_username_sudah_ada(username, self.user_yang_diedit):
                self.show_warning("Gagal", "Username sudah dipakai user lain.")
                return
            
            if update_user(self.user_yang_diedit, username, 
                          password if password else None, role):
                self.show_success("Berhasil", "Data user berhasil diupdate.")
                self.bersihkan_form()
                self.muat_user()
            else:
                self.show_error("Error", "Gagal update user.")
    
    def edit_user(self, id_user):
        """Load data user ke form untuk edit"""
        for row in range(self.table_user.rowCount()):
            if self.table_user.item(row, 0).text() == str(id_user):
                username = self.table_user.item(row, 1).text()
                role_text = self.table_user.item(row, 2).text().lower()
                
                self.input_username.setText(username)
                self.input_password.clear()
                self.input_password.setPlaceholderText("Kosongkan jika tidak ganti password")
                
                index = self.combo_role.findData(role_text)
                if index >= 0:
                    self.combo_role.setCurrentIndex(index)
                
                self.user_yang_diedit = id_user
                self.btn_simpan.setText("Update User")
                
                style = StyleManager()
                self.btn_simpan.setStyleSheet(style.get_button_style('warning'))
                
                self.input_username.setFocus()
                break
    
    def hapus_user(self, id_user):
        """Hapus user"""
        if not self.confirm_action("Hapus User", "Yakin hapus user ini?"):
            return
        
        hapus_user(id_user)
        self.muat_user()
        self.bersihkan_form()
    
    def bersihkan_form(self):
        """Reset form ke state awal"""
        self.input_username.clear()
        self.input_password.clear()
        self.input_password.setPlaceholderText("Isi password...")
        self.combo_role.setCurrentIndex(0)
        self.user_yang_diedit = None
        
        self.btn_simpan.setText("Simpan Data")
        
        style = StyleManager()
        self.btn_simpan.setStyleSheet(style.get_button_style('success'))
        
        self.input_username.setFocus()