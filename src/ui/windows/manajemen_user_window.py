"""
Manajemen User Window - SmartNavigation
========================================
User CRUD dengan form + table memory navigation
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QLabel, 
    QPushButton, QFormLayout, QComboBox, QFrame
)
from PyQt6.QtCore import Qt

from src.ui.base.base_window import BaseWindow
from src.ui.base.style_manager import StyleManager
from src.ui.widgets.smart_table import SmartTable
from src.database import (
    semua_user, tambah_user_baru, update_user, 
    hapus_user, cek_username_sudah_ada
)


class ManajemenUserWindow(BaseWindow):
    """User management dengan navigation memory"""
    
    def __init__(self):
        super().__init__()
        
        self.user_yang_diedit = None
        self.last_form_widget = None  # Track last form focus untuk memory navigation
        
        self.setup_ui()
        self.setup_navigation()
        
        self.setWindowTitle("Manajemen Pengguna (Admin Only)")
        self.setGeometry(100, 100, 950, 550)
        
        self.muat_user()
    
    def setup_ui(self):
        """Setup UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # LEFT: Form
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
        self.btn_batal.setStyleSheet(style.get_button_style('default'))
        self.btn_batal.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_batal.clicked.connect(self.bersihkan_form)
        
        btn_layout.addWidget(self.btn_simpan)
        btn_layout.addWidget(self.btn_batal)
        form_layout.addLayout(btn_layout)
        
        form_layout.addStretch()
        
        lbl_nav = QLabel("↑↓=Form | ←→=Form↔Table |\n Space=Combo | F2=Edit | Del=Hapus")
        lbl_nav.setStyleSheet(
            "color:#777; font-size:11px; background:transparent; border:none;"
        )
        form_layout.addWidget(lbl_nav)
        
        layout.addWidget(form_container)
        
        # RIGHT: Table
        table_container = QVBoxLayout()
        
        lbl_tabel = QLabel("Daftar Pengguna Sistem:")
        lbl_tabel.setStyleSheet(
            "font-size: 14px; font-weight: bold; margin-bottom: 5px; color: #ddd;"
        )
        table_container.addWidget(lbl_tabel)
        
        self.table_user = SmartTable(0, 4)
        self.table_user.setHorizontalHeaderLabels(["ID", "Username", "Role", "Aksi"])
        self.table_user.setColumnHidden(0, True)
        self.table_user.stretch_column(1)
        
        table_container.addWidget(self.table_user)
        layout.addLayout(table_container)
        
        self.input_username.setFocus()
    
    def setup_navigation(self):
        """
        Navigation dengan memory:
        - Form → Table (Right) - ingat posisi form
        - Table → Form (Left) - kembali ke posisi terakhir
        """
        
        # Username: Down/Enter → Password, Right → Table
        self.register_navigation(self.input_username, {
            Qt.Key.Key_Down: self.input_password,
            Qt.Key.Key_Return: self.input_password,
            Qt.Key.Key_Right: lambda: self._go_to_table(self.input_username)
        })
        
        # Password: Up → Username, Down/Enter → Combo, Right → Table
        self.register_navigation(self.input_password, {
            Qt.Key.Key_Up: self.input_username,
            Qt.Key.Key_Down: self.combo_role,
            Qt.Key.Key_Return: lambda: (self.combo_role.setFocus(), self.combo_role.showPopup()),
            Qt.Key.Key_Right: lambda: self._go_to_table(self.input_password)
        })
        
        # Combo Role: Up → Password, Down/Space → Open dropdown, Return → Button, Right → Table
        self.register_navigation(self.combo_role, {
            Qt.Key.Key_Up: self.input_password,
            Qt.Key.Key_Down: lambda: self.combo_role.showPopup(),
            Qt.Key.Key_Space: lambda: self.combo_role.showPopup(),
            Qt.Key.Key_Return: self.btn_simpan,
            Qt.Key.Key_Right: lambda: self._go_to_table(self.combo_role)
        })
        
        # Button Simpan: Up → Combo, Right → Table, Enter → Save
        self.register_navigation(self.btn_simpan, {
            Qt.Key.Key_Up: self.combo_role,
            Qt.Key.Key_Right: self.btn_batal,
            Qt.Key.Key_Return: self.simpan_user
        })
        
        # Button Batal: Up → Combo, Left → Simpan, Right → Table, Enter → Reset
        self.register_navigation(self.btn_batal, {
            Qt.Key.Key_Up: self.combo_role,
            Qt.Key.Key_Left: self.btn_simpan,
            Qt.Key.Key_Right: lambda: self._go_to_table(self.btn_batal),
            Qt.Key.Key_Return: self.bersihkan_form
        })
        
        # Table: F2/Enter → Edit, Delete → Hapus, Left → Back to form
        self.register_table_callbacks(self.table_user, {
            'edit': self.edit_current_row,
            'delete': self.delete_current_row,
            'focus_up': self.input_username
        })
        
        # Table Left arrow → Kembali ke form (dengan memory)
        self.register_navigation(self.table_user, {
            Qt.Key.Key_Left: self._back_to_form
        })
    
    # ========== MEMORY NAVIGATION HELPERS ==========
    
    def _go_to_table(self, from_widget):
        """Go to table dan ingat dari widget mana"""
        self.last_form_widget = from_widget
        self.focus_table_first_row(self.table_user)
    
    def _back_to_form(self):
        """Kembali ke form widget terakhir"""
        if self.last_form_widget:
            self.last_form_widget.setFocus()
        else:
            self.input_username.setFocus()
    
    # ========== TABLE HELPERS ==========
    
    def edit_current_row(self):
        """Edit user from table (F2/Enter)"""
        row = self.table_user.currentRow()
        if row >= 0:
            user_id = self.table_user.item(row, 0).text()
            self.edit_user(user_id)
    
    def delete_current_row(self):
        """Delete user from table (Delete key)"""
        row = self.table_user.currentRow()
        if row >= 0:
            user_id = self.table_user.item(row, 0).text()
            self.hapus_user(user_id)
    
    # ========== DATA OPERATIONS ==========
    
    def muat_user(self):
        """Load all users to table"""
        self.table_user.clear_table()
        user_list = semua_user()
        
        from PyQt6.QtWidgets import QTableWidgetItem
        
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
            
            # Action buttons in table
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
        """Save new or update existing user"""
        username = self.input_username.text().strip()
        password = self.input_password.text().strip()
        role = self.combo_role.currentData()
        
        if not username:
            self.show_warning("Input", "Username harus diisi.")
            self.input_username.setFocus()
            return
        
        # Add new user
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
        
        # Update existing user
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
        """Load user data to form for editing"""
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
        """Delete user with confirmation"""
        if not self.confirm_action("Hapus User", "Yakin hapus user ini?"):
            return
        
        hapus_user(id_user)
        self.muat_user()
        self.bersihkan_form()
    
    def bersihkan_form(self):
        """Reset form to add mode"""
        self.clear_form(self.input_username, self.input_password)
        self.input_password.setPlaceholderText("Isi password...")
        self.combo_role.setCurrentIndex(0)
        self.user_yang_diedit = None
        
        self.btn_simpan.setText("Simpan Data")
        
        style = StyleManager()
        self.btn_simpan.setStyleSheet(style.get_button_style('success'))
        
        self.input_username.setFocus()