from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QHBoxLayout,
    QLineEdit, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QFormLayout, QComboBox, QHeaderView, QAbstractItemView, QFrame
)
from PyQt6.QtCore import Qt, QEvent
from src.database import (
    semua_user, tambah_user_baru, update_user, hapus_user, cek_username_sudah_ada
)

class ManajemenUserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manajemen Pengguna (Admin Only)")
        self.setGeometry(100, 100, 950, 550) # Sedikit diperlebar agar info muat

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # --- STYLING DARK MODE ---
        central_widget.setStyleSheet("""
            QWidget { 
                background-color: #121212; 
                color: #e0e0e0; 
                font-family: 'Segoe UI', sans-serif; 
                font-size: 13px;
                outline: none;
            }
            QLabel { font-size: 14px; }
            
            QLineEdit, QComboBox { 
                background-color: #1E1E1E; border: 1px solid #333; 
                border-radius: 5px; padding: 10px; color: white;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #29b6f6; background-color: #252525;
            }
            
            QTableWidget {
                background-color: #1E1E1E; gridline-color: #333;
                border: 1px solid #333; border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #252525; color: white;
                padding: 8px; border: none; font-weight: bold;
            }
            QTableWidget::item:selected {
                background-color: #00E5FF; color: #000000;
            }
            QTableWidget:focus { border: 2px solid #29b6f6; }
        """)
        
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # --- KIRI: FORM ---
        form_container = QFrame()
        form_container.setFixedWidth(320)
        form_container.setStyleSheet("background-color: #181818; border-radius: 10px; border: 1px solid #333;")
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_judul = QLabel("📝 Form Pengguna")
        lbl_judul.setStyleSheet("font-size: 18px; font-weight: bold; color: #29b6f6; border: none; margin-bottom: 10px; background: transparent;")
        form_layout.addWidget(lbl_judul)

        input_group = QFormLayout()
        input_group.setVerticalSpacing(15)
        
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Masukkan username")
        self.input_username.installEventFilter(self) 
        
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setPlaceholderText("Isi password...")
        self.input_password.installEventFilter(self) 
        
        self.combo_role = QComboBox()
        self.combo_role.addItem("Kasir", "kasir") 
        self.combo_role.addItem("Administrator", "admin")
        self.combo_role.setCursor(Qt.CursorShape.PointingHandCursor)
        self.combo_role.installEventFilter(self) 
        
        lbl_style = "font-weight: bold; color: #bbb; border: none; background: transparent;"
        input_group.addRow(QLabel("Username:", styleSheet=lbl_style), self.input_username)
        input_group.addRow(QLabel("Password:", styleSheet=lbl_style), self.input_password)
        input_group.addRow(QLabel("Role:", styleSheet=lbl_style), self.combo_role)
        
        form_layout.addLayout(input_group)
        form_layout.addSpacing(25)
        
        # Tombol Aksi
        btn_layout = QHBoxLayout()
        
        self.btn_simpan = QPushButton("Simpan Data")
        self.btn_simpan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_simpan.setStyleSheet("""
            QPushButton { 
                background-color: #4CAF50; color: white; border: none; 
                padding: 12px; border-radius: 5px; font-weight: bold; 
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:focus { border: 3px solid #FFEB3B; background-color: #43A047; }
        """)
        self.btn_simpan.clicked.connect(self.simpan_user)
        self.btn_simpan.installEventFilter(self) 
        
        self.btn_batal = QPushButton("Reset")
        self.btn_batal.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_batal.setStyleSheet("""
            QPushButton { 
                background-color: #424242; color: white; border: none; 
                padding: 12px; border-radius: 5px; 
            }
            QPushButton:hover { background-color: #616161; }
            QPushButton:focus { border: 3px solid #FFEB3B; }
        """)
        self.btn_batal.clicked.connect(self.bersihkan_form)
        self.btn_batal.installEventFilter(self) 
        
        btn_layout.addWidget(self.btn_simpan)
        btn_layout.addWidget(self.btn_batal)
        form_layout.addLayout(btn_layout)
        
        form_layout.addStretch()
        
        # [DIPULIHKAN & DILENGKAPI] Label Instruksi Navigasi
        lbl_info = QLabel(
            "💡 <b>Tips Keyboard:</b><br>"
            "- <b>Enter</b>: Pindah Kolom / Simpan<br>"
            "- <b>Ctrl + Bawah</b>: Loncat ke Tabel<br>"
            "- <b>Ctrl + Atas</b>: Loncat ke Username<br>"
            "- <b>F2</b>: Edit User | <b>Del</b>: Hapus User<br>"
            "- <b>ESC</b>: Tutup Menu"
        )
        lbl_info.setWordWrap(True)
        lbl_info.setStyleSheet("color: #888; font-size: 11px; border: none; font-style: italic; background: transparent;")
        form_layout.addWidget(lbl_info)

        layout.addWidget(form_container)

        # --- KANAN: TABEL ---
        table_container = QVBoxLayout()
        lbl_tabel = QLabel("Daftar Pengguna Sistem:")
        lbl_tabel.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 5px; color: #ddd;")
        table_container.addWidget(lbl_tabel)

        self.table_user = QTableWidget(0, 4)
        self.table_user.setHorizontalHeaderLabels(["ID", "Username", "Role", "Aksi"])
        self.table_user.setColumnHidden(0, True) 
        self.table_user.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_user.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_user.verticalHeader().setVisible(False)
        self.table_user.setShowGrid(False)
        self.table_user.setAlternatingRowColors(True)
        self.table_user.setStyleSheet("QTableWidget { alternate-background-color: #252525; background-color: #1E1E1E; }")
        self.table_user.installEventFilter(self) 
        
        header = self.table_user.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        table_container.addWidget(self.table_user)
        layout.addLayout(table_container)

        self.muat_user()
        self.user_yang_diedit = None 
        
        self.installEventFilter(self)

    # --- LOGIKA KEYBOARD ---
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            
            # [SHORTCUT GLOBAL]
            if event.key() == Qt.Key.Key_Escape:
                self.close()
                return True

            if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Down:
                if self.table_user.rowCount() > 0:
                    self.table_user.setFocus()
                    self.table_user.selectRow(0)
                return True

            if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Up:
                self.input_username.setFocus()
                self.input_username.selectAll()
                return True

            # 1. INPUT USERNAME
            if obj == self.input_username:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Down):
                    self.input_password.setFocus()
                    return True
            
            # 2. INPUT PASSWORD
            elif obj == self.input_password:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Down):
                    self.combo_role.setFocus()
                    self.combo_role.showPopup() 
                    return True
                elif event.key() == Qt.Key.Key_Up:
                    self.input_username.setFocus()
                    return True

            # 3. COMBO BOX ROLE
            elif obj == self.combo_role:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Down):
                    self.btn_simpan.setFocus()
                    return True
                elif event.key() == Qt.Key.Key_Up:
                    self.input_password.setFocus()
                    return True

            # 4. TOMBOL SIMPAN
            elif obj == self.btn_simpan:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self.btn_simpan.click()
                    return True
                if event.key() == Qt.Key.Key_Right: self.btn_batal.setFocus(); return True
                elif event.key() == Qt.Key.Key_Up: self.combo_role.setFocus(); return True
                elif event.key() == Qt.Key.Key_Down: 
                    if self.table_user.rowCount() > 0:
                        self.table_user.setFocus()
                        self.table_user.selectRow(0)
                    return True

            # 5. TOMBOL RESET
            elif obj == self.btn_batal:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self.btn_batal.click()
                    return True
                if event.key() == Qt.Key.Key_Left: self.btn_simpan.setFocus(); return True
                elif event.key() == Qt.Key.Key_Up: self.combo_role.setFocus(); return True
                elif event.key() == Qt.Key.Key_Down:
                    if self.table_user.rowCount() > 0:
                        self.table_user.setFocus()
                        self.table_user.selectRow(0)
                    return True

            # 6. TABEL USER
            elif obj == self.table_user:
                if event.key() == Qt.Key.Key_F2:
                    self.edit_current_row()
                    return True
                elif event.key() == Qt.Key.Key_Delete:
                    self.delete_current_row()
                    return True
                if event.key() == Qt.Key.Key_Up and self.table_user.currentRow() == 0:
                    self.btn_simpan.setFocus() 
                    return True

        return super().eventFilter(obj, event)

    def edit_current_row(self):
        row = self.table_user.currentRow()
        if row >= 0:
            id_user = self.table_user.item(row, 0).text()
            self.edit_user(id_user)

    def delete_current_row(self):
        row = self.table_user.currentRow()
        if row >= 0:
            id_user = self.table_user.item(row, 0).text()
            self.hapus_user(id_user)

    def muat_user(self):
        self.table_user.setRowCount(0)
        user_list = semua_user()
        
        for row, (id_user, username, role) in enumerate(user_list):
            self.table_user.insertRow(row)
            self.table_user.setItem(row, 0, QTableWidgetItem(str(id_user)))
            self.table_user.setItem(row, 1, QTableWidgetItem(username))
            
            role_item = QTableWidgetItem(role.upper())
            role_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if role == 'admin': role_item.setForeground(Qt.GlobalColor.cyan)
            else: role_item.setForeground(Qt.GlobalColor.yellow)
            
            self.table_user.setItem(row, 2, role_item)
            
            btn_container = QWidget()
            btn_container.setStyleSheet("background: transparent; outline: none; border: none;") 
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(5, 2, 5, 2)
            btn_layout.setSpacing(5)
            
            btn_edit = QPushButton("Edit")
            btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_edit.setStyleSheet("""
                QPushButton { background-color: #FF9800; color: white; border-radius: 3px; font-size: 11px; outline: none; border: none;}
                QPushButton:focus { border: 1px solid #E65100; }
            """)
            btn_edit.clicked.connect(lambda checked, uid=id_user: self.edit_user(uid))
            
            btn_hapus = QPushButton("Hapus")
            btn_hapus.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_hapus.setStyleSheet("""
                QPushButton { background-color: #f44336; color: white; border-radius: 3px; font-size: 11px; outline: none; border: none; }
                QPushButton:focus { border: 1px solid #B71C1C; }
            """)
            btn_hapus.clicked.connect(lambda checked, uid=id_user: self.hapus_user(uid))
            
            btn_layout.addWidget(btn_edit)
            btn_layout.addWidget(btn_hapus)
            self.table_user.setCellWidget(row, 3, btn_container)

    def simpan_user(self):
        username = self.input_username.text().strip()
        password = self.input_password.text().strip()
        role = self.combo_role.currentData() 
        
        if not username:
            QMessageBox.warning(self, "Input", "Username harus diisi.")
            self.input_username.setFocus()
            return
        
        if self.user_yang_diedit is None:
            if not password:
                QMessageBox.warning(self, "Input", "Password wajib untuk user baru.")
                self.input_password.setFocus()
                return
            if cek_username_sudah_ada(username):
                QMessageBox.warning(self, "Gagal", f"Username '{username}' sudah ada.")
                self.input_username.setFocus()
                return
            
            if tambah_user_baru(username, password, role):
                QMessageBox.information(self, "Berhasil", "User ditambahkan.")
                self.bersihkan_form()
                self.muat_user()
            else:
                QMessageBox.critical(self, "Error", "Gagal menyimpan.")
        else:
            if cek_username_sudah_ada(username, self.user_yang_diedit):
                QMessageBox.warning(self, "Gagal", "Username sudah ada.")
                return
                
            if update_user(self.user_yang_diedit, username, password if password else None, role):
                QMessageBox.information(self, "Berhasil", "Data diupdate.")
                self.bersihkan_form()
                self.muat_user()
            else:
                QMessageBox.critical(self, "Error", "Gagal update.")

    def edit_user(self, id_user):
        for row in range(self.table_user.rowCount()):
            if self.table_user.item(row, 0).text() == str(id_user):
                username = self.table_user.item(row, 1).text()
                role_text = self.table_user.item(row, 2).text().lower() 
                
                self.input_username.setText(username)
                self.input_password.clear() 
                self.input_password.setPlaceholderText("Kosongkan jika tidak ganti pass")
                
                index = self.combo_role.findData(role_text)
                if index >= 0: self.combo_role.setCurrentIndex(index)
                
                self.user_yang_diedit = id_user
                self.btn_simpan.setText("Update User")
                self.btn_simpan.setStyleSheet("""
                    QPushButton { background-color: #FF9800; color: white; border: none; padding: 12px; border-radius: 5px; font-weight: bold; outline: none; }
                    QPushButton:focus { border: 3px solid #FFF; }
                """)
                self.input_username.setFocus()
                break

    def hapus_user(self, id_user):
        reply = QMessageBox.question(self, "Hapus", "Yakin hapus user ini?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            hapus_user(id_user)
            self.muat_user()
            self.bersihkan_form()

    def bersihkan_form(self):
        self.input_username.clear()
        self.input_password.clear()
        self.input_password.setPlaceholderText("Isi password...")
        self.combo_role.setCurrentIndex(0)
        self.user_yang_diedit = None
        self.btn_simpan.setText("Simpan Data")
        self.btn_simpan.setStyleSheet("""
            QPushButton { background-color: #4CAF50; color: white; border: none; padding: 12px; border-radius: 5px; font-weight: bold; outline: none; }
            QPushButton:focus { border: 3px solid #FFEB3B; }
        """)
        self.input_username.setFocus()

    def set_current_user(self, username):
        self.current_user = username