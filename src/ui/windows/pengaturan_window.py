"""
Pengaturan Window - SmartNavigation
====================================
Vertical form: 4 fields + button
Arrow Up/Down navigation
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
    """Store settings dengan vertical navigation"""
    
    def __init__(self):
        super().__init__()
        
        self.setup_ui()
        self.setup_navigation()
        self.muat_data()
        
        self.setWindowTitle("Pengaturan Toko")
        self.setGeometry(100, 100, 600, 600)
    
    def setup_ui(self):
        """Setup UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        lbl_judul = QLabel("🔧 Konfigurasi Toko")
        lbl_judul.setStyleSheet("font-size: 20px; color: #2196F3; margin-bottom: 10px;")
        layout.addWidget(lbl_judul)
        
        # Form container
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
        
        # Input fields
        self.inp_nama = QLineEdit()
        self.inp_nama.setPlaceholderText("Nama Toko")
        
        self.inp_alamat = QLineEdit()
        self.inp_alamat.setPlaceholderText("Alamat Lengkap")
        
        self.inp_telp = QLineEdit()
        self.inp_telp.setPlaceholderText("No. Telepon / HP")
        
        self.inp_footer = QTextEdit()
        self.inp_footer.setPlaceholderText("Pesan di bagian bawah struk...")
        self.inp_footer.setFixedHeight(100)
        
        lbl_style = "font-weight: bold; color: #888; border: none;"
        form_layout.addRow(QLabel("Nama Toko:", styleSheet=lbl_style), self.inp_nama)
        form_layout.addRow(QLabel("Alamat:", styleSheet=lbl_style), self.inp_alamat)
        form_layout.addRow(QLabel("Telepon:", styleSheet=lbl_style), self.inp_telp)
        form_layout.addRow(QLabel("Footer Struk:", styleSheet=lbl_style), self.inp_footer)
        
        layout.addWidget(form_frame)
        
        lbl_info = QLabel("💡 ↑↓=Navigate | Enter=Next | Ctrl+S=Save | ESC=Close")
        lbl_info.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
        layout.addWidget(lbl_info)
        
        layout.addStretch()
        
        # Save button
        style = StyleManager()
        self.btn_simpan = QPushButton("💾 Simpan Perubahan (Ctrl+S)")
        self.btn_simpan.setStyleSheet(style.get_button_style('success'))
        self.btn_simpan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_simpan.clicked.connect(self.simpan_data)
        layout.addWidget(self.btn_simpan)
        
        self.inp_nama.setFocus()
    
    def setup_navigation(self):
        """
        Vertical navigation chain
        Up/Down arrows untuk pindah field
        """
        # Nama: Down/Enter → Alamat
        self.register_navigation(self.inp_nama, {
            Qt.Key.Key_Down: self.inp_alamat,
            Qt.Key.Key_Return: self.inp_alamat
        })
        
        # Alamat: Up → Nama, Down/Enter → Telepon
        self.register_navigation(self.inp_alamat, {
            Qt.Key.Key_Up: self.inp_nama,
            Qt.Key.Key_Down: self.inp_telp,
            Qt.Key.Key_Return: self.inp_telp
        })
        
        # Telepon: Up → Alamat, Down/Enter → Footer
        self.register_navigation(self.inp_telp, {
            Qt.Key.Key_Up: self.inp_alamat,
            Qt.Key.Key_Down: self.inp_footer,
            Qt.Key.Key_Return: self.inp_footer
        })
        
        # Footer: Up → Telepon, Down → Button
        # Note: Enter di TextEdit untuk new line, jadi tidak di-register
        self.register_navigation(self.inp_footer, {
            Qt.Key.Key_Up: self.inp_telp,
            Qt.Key.Key_Down: self.btn_simpan
        })
        
        # Button: Up → Footer, Enter → Save
        self.register_navigation(self.btn_simpan, {
            Qt.Key.Key_Up: self.inp_footer,
            Qt.Key.Key_Return: self.simpan_data
        })
    
    def muat_data(self):
        """Load settings from file"""
        data = load_settings()
        self.inp_nama.setText(data.get("nama_toko", ""))
        self.inp_alamat.setText(data.get("alamat_toko", ""))
        self.inp_telp.setText(data.get("telepon", ""))
        self.inp_footer.setText(data.get("footer_struk", ""))
    
    def simpan_data(self):
        """Save settings"""
        data = {
            "nama_toko": self.inp_nama.text().strip(),
            "alamat_toko": self.inp_alamat.text().strip(),
            "telepon": self.inp_telp.text().strip(),
            "footer_struk": self.inp_footer.toPlainText().strip()
        }
        
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
    
    def simpan(self):
        """Alias for Ctrl+S"""
        self.simpan_data()