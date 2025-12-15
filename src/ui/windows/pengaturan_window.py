from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, 
    QPushButton, QFormLayout, QMessageBox, QFrame, QTextEdit
)
from PyQt6.QtCore import Qt, QEvent
from src.settings import load_settings, save_settings

class PengaturanWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pengaturan Toko")
        self.setGeometry(100, 100, 600, 600) # Ukuran pas

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # --- DARK MODE & STYLING BERSIH ---
        central_widget.setStyleSheet("""
            QWidget { 
                background-color: #121212; 
                color: #e0e0e0; 
                font-family: 'Segoe UI', sans-serif; 
                font-size: 13px;
                outline: none; /* Hapus garis fokus bawaan */
            }
            
            /* Input Line (Satu Baris) */
            QLineEdit { 
                background-color: #1E1E1E; 
                border: 1px solid #333; 
                padding: 10px; 
                color: white; 
                border-radius: 5px;
            }
            QLineEdit:focus { border: 2px solid #2196F3; background-color: #252525; }
            
            /* Input Text (Multi Baris) */
            QTextEdit { 
                background-color: #1E1E1E; 
                border: 1px solid #333; 
                padding: 10px; 
                color: white; 
                border-radius: 5px;
            }
            QTextEdit:focus { border: 2px solid #2196F3; background-color: #252525; }
            
            /* Tombol */
            QPushButton { 
                background-color: #4CAF50; 
                color: white; 
                border: none; 
                padding: 12px; 
                border-radius: 5px; 
                font-weight: bold; 
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:focus { 
                border: 2px solid #fff; /* Fokus Putih Jelas */
                background-color: #43A047;
            }
            
            QLabel { font-weight: bold; color: #bbb; background: transparent; }
        """)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(30, 30, 30, 30)

        # Judul
        lbl_judul = QLabel("🔧 Konfigurasi Toko")
        lbl_judul.setStyleSheet("font-size: 20px; color: #2196F3; margin-bottom: 10px;")
        layout.addWidget(lbl_judul)

        # Form Container
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: #181818; border-radius: 10px; border: 1px solid #333;")
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)

        # Input Fields
        self.inp_nama = QLineEdit()
        self.inp_nama.setPlaceholderText("Nama Toko")
        self.inp_nama.installEventFilter(self)

        self.inp_alamat = QLineEdit()
        self.inp_alamat.setPlaceholderText("Alamat Lengkap")
        self.inp_alamat.installEventFilter(self)

        self.inp_telp = QLineEdit()
        self.inp_telp.setPlaceholderText("No. Telepon / HP")
        self.inp_telp.installEventFilter(self)

        self.inp_footer = QTextEdit()
        self.inp_footer.setPlaceholderText("Pesan di bagian bawah struk...")
        self.inp_footer.setFixedHeight(100)
        self.inp_footer.installEventFilter(self)

        # Label Style
        lbl_style = "font-weight: bold; color: #888; border: none;"
        
        form_layout.addRow(QLabel("Nama Toko:", styleSheet=lbl_style), self.inp_nama)
        form_layout.addRow(QLabel("Alamat:", styleSheet=lbl_style), self.inp_alamat)
        form_layout.addRow(QLabel("Telepon:", styleSheet=lbl_style), self.inp_telp)
        form_layout.addRow(QLabel("Footer Struk:", styleSheet=lbl_style), self.inp_footer)

        layout.addWidget(form_frame)
        
        # Info Navigasi
        lbl_info = QLabel("💡 Info: Gunakan Enter/Panah untuk pindah. (Footer gunakan Tab/Ctrl+Bawah)")
        lbl_info.setStyleSheet("color: #666; font-size: 11px; font-style: italic; margin-top: 5px;")
        layout.addWidget(lbl_info)
        
        layout.addStretch()

        # Tombol Simpan
        self.btn_simpan = QPushButton("Simpan Perubahan")
        self.btn_simpan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_simpan.clicked.connect(self.simpan_data)
        self.btn_simpan.installEventFilter(self)
        layout.addWidget(self.btn_simpan)

        # Load Data Awal
        self.muat_data()
        self.inp_nama.setFocus() # Fokus awal

    def muat_data(self):
        data = load_settings()
        self.inp_nama.setText(data.get("nama_toko", ""))
        self.inp_alamat.setText(data.get("alamat_toko", ""))
        self.inp_telp.setText(data.get("telepon", ""))
        self.inp_footer.setText(data.get("footer_struk", ""))

    def simpan_data(self):
        data = {
            "nama_toko": self.inp_nama.text().strip(),
            "alamat_toko": self.inp_alamat.text().strip(),
            "telepon": self.inp_telp.text().strip(),
            "footer_struk": self.inp_footer.toPlainText().strip()
        }
        
        if not data["nama_toko"]:
            QMessageBox.warning(self, "Error", "Nama Toko wajib diisi!")
            self.inp_nama.setFocus()
            return

        try:
            save_settings(data)
            QMessageBox.information(self, "Sukses", "Pengaturan berhasil disimpan!")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan: {e}")

    # --- LOGIKA KEYBOARD ---
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            
            # ESC -> Tutup
            if event.key() == Qt.Key.Key_Escape:
                self.close()
                return True

            # 1. INPUT NAMA
            if obj == self.inp_nama:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Down):
                    self.inp_alamat.setFocus()
                    return True
            
            # 2. INPUT ALAMAT
            elif obj == self.inp_alamat:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Down):
                    self.inp_telp.setFocus()
                    return True
                elif event.key() == Qt.Key.Key_Up:
                    self.inp_nama.setFocus()
                    return True

            # 3. INPUT TELEPON
            elif obj == self.inp_telp:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Down):
                    self.inp_footer.setFocus()
                    return True
                elif event.key() == Qt.Key.Key_Up:
                    self.inp_alamat.setFocus()
                    return True

            # 4. INPUT FOOTER (TEXT EDIT)
            # Khusus ini: Enter = Baris Baru. Pindah pakai Tab atau Ctrl+Bawah
            elif obj == self.inp_footer:
                if event.key() == Qt.Key.Key_Tab or (event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Down):
                    self.btn_simpan.setFocus()
                    return True
                # Ctrl+Atas untuk balik ke Telepon
                elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Up:
                    self.inp_telp.setFocus()
                    return True

            # 5. TOMBOL SIMPAN
            elif obj == self.btn_simpan:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self.btn_simpan.click()
                    return True
                elif event.key() == Qt.Key.Key_Up:
                    self.inp_footer.setFocus()
                    return True

        return super().eventFilter(obj, event)