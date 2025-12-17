"""
Preview Struk Dialog
====================
Dialog untuk preview struk sebelum print
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit
)
from PyQt6.QtCore import Qt, QEvent

class PreviewDialog(QDialog):
    """
    Dialog preview struk transaksi
    
    Returns:
        accepted: bool - True jika user klik "Print & Buka PDF"
        user_print: bool - Flag apakah user mau print
    """
    
    def __init__(self, no_faktur, tanggal, kasir, keranjang, total, 
                 uang_diterima, kembalian, parent=None):
        super().__init__(parent)
        
        self.no_faktur = no_faktur
        self.tanggal = tanggal
        self.kasir = kasir
        self.keranjang = keranjang
        self.total = total
        self.uang_diterima = uang_diterima
        self.kembalian = kembalian
        self.user_print = False
        
        self.setup_ui()
        
        # Window properties
        self.setWindowTitle("Preview Struk Transaksi")
        self.setFixedSize(500, 600)
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Styling
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333;
            }
            QTextEdit {
                background-color: white;
                color: #000000;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                padding: 10px;
            }
            QPushButton {
                padding: 12px 24px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
                border: 3px solid transparent;
                outline: none;
            }
            QPushButton#btnPrint {
                background-color: #4CAF50;
                color: white;
                border: none;
            }
            QPushButton#btnPrint:hover {
                background-color: #45a049;
            }
            QPushButton#btnPrint:focus {
                border: 3px solid #FFD700;  /* Gold border */
                background-color: #45a049;
                /* transform: scale(1.05);
                box-shadow: 0 0 10px rgba(255, 215, 0, 0.5); */
            }
            QPushButton#btnClose {
                background-color: #757575;
                color: white;
                border: none;
            }
            QPushButton#btnClose:hover {
                background-color: #616161;
            }
            QPushButton#btnClose:focus {
                border: 3px solid #FFD700;  /* Gold border */
                background-color: #616161;
                /* transform: scale(1.05);
                box-shadow: 0 0 10px rgba(255, 215, 0, 0.5); */
            }
        """)
        
        # Header
        lbl_header = QLabel("📄 PREVIEW STRUK TRANSAKSI")
        lbl_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #1976D2; margin-bottom: 10px;")
        lbl_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_header)
        
        # Text Preview
        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(True)
        self.render_preview()
        layout.addWidget(self.text_preview)
        
        # Info
        lbl_info = QLabel("💡 Periksa transaksi sebelum mencetak")
        lbl_info.setStyleSheet("font-size: 10px; color: #666; font-style: italic;")
        lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_print = QPushButton("🖨️ Print & Buka PDF")
        self.btn_print.setObjectName("btnPrint")
        self.btn_print.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_print.clicked.connect(self.confirm_print)
        self.btn_print.setAutoDefault(True)
        self.btn_print.setDefault(True)
        self.btn_print.installEventFilter(self)
        
        self.btn_close = QPushButton("✖️ Tutup")
        self.btn_close.setObjectName("btnClose")
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(self.reject)
        self.btn_close.installEventFilter(self)
        
        btn_layout.addWidget(self.btn_print)
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)
        
        # Focus ke tombol print
        self.btn_print.setFocus()

    def render_preview(self):
        """Render preview struk dalam format text"""
        from src.settings import load_settings
        
        settings = load_settings()
        nama_toko = settings.get("nama_toko", "Toko Tanpa Nama")
        alamat_toko = settings.get("alamat_toko", "")
        telepon = settings.get("telepon", "")
        
        preview_text = ""
        preview_text += "=" * 50 + "\n"
        preview_text += f"{nama_toko.center(50)}\n"
        if alamat_toko:
            preview_text += f"{alamat_toko.center(50)}\n"
        if telepon:
            preview_text += f"Telp: {telepon}".center(50) + "\n"
        preview_text += "=" * 50 + "\n\n"
        
        # Info transaksi
        preview_text += f"No. Faktur : {self.no_faktur}\n"
        preview_text += f"Tanggal    : {self.tanggal}\n"
        preview_text += f"Kasir      : {self.kasir}\n"
        preview_text += "=" * 50 + "\n\n"
        
        # Items
        subtotal_all = 0
        
        for item in self.keranjang:
            # item = (nama, harga, jumlah, subtotal)
            nama = item[0]
            harga = item[1]
            jumlah = item[2]
            subtotal = item[3]
            
            preview_text += f"{nama}\n"
            preview_text += f"  {jumlah} x Rp {int(harga):,}".ljust(30)
            preview_text += f"Rp {int(subtotal):,}\n\n"
            
            subtotal_all += subtotal
        
        preview_text += "-" * 50 + "\n"
        
        # Total
        preview_text += "TOTAL".ljust(30) + f"Rp {int(self.total):,}".rjust(20) + "\n"
        preview_text += "=" * 50 + "\n\n"
        
        # Pembayaran
        preview_text += "TUNAI".ljust(30) + f"Rp {int(self.uang_diterima):,}".rjust(20) + "\n"
        preview_text += "KEMBALIAN".ljust(30) + f"Rp {int(self.kembalian):,}".rjust(20) + "\n"
        preview_text += "=" * 50 + "\n"
        
        self.text_preview.setText(preview_text)
    
    def confirm_print(self):
        """User konfirmasi mau print"""
        self.user_print = True
        self.accept()
    
    def eventFilter(self, obj, event):
        """Handle keyboard navigation untuk tombol"""
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            
            # Tombol Print
            if obj == self.btn_print:
                if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
                    self.confirm_print()
                    return True
                if key == Qt.Key.Key_Right:
                    self.btn_close.setFocus()
                    return True
            
            # Tombol Close
            elif obj == self.btn_close:
                if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
                    self.reject()
                    return True
                if key == Qt.Key.Key_Left:
                    self.btn_print.setFocus()
                    return True
                # Left = Previous button
                if key == Qt.Key.Key_Left:
                    self.btn_print.setFocus()
                    return True
                
                # Shift+Tab = Previous button
                if key == Qt.Key.Key_Backtab:  # Shift+Tab
                    self.btn_print.setFocus()
                    return True
        
        return super().eventFilter(obj, event)
    
    def keyPressEvent(self, event):
        """Handle ESC key"""
        key = event.key()
        
        # ESC = Close
        if key == Qt.Key.Key_Escape:
            self.reject()
            return
        
        # Tab navigation (kalau tidak ter-handle di eventFilter)
        if key == Qt.Key.Key_Tab:
            if self.btn_print.hasFocus():
                self.btn_close.setFocus()
            else:
                self.btn_print.setFocus()
            return
        
        # Shift+Tab
        if key == Qt.Key.Key_Backtab:
            if self.btn_close.hasFocus():
                self.btn_print.setFocus()
            else:
                self.btn_close.setFocus()
            return
        
        # Pass ke parent untuk handling lainnya
        super().keyPressEvent(event)