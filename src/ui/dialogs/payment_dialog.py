"""
Payment Dialog
==============
Dialog untuk input pembayaran dengan validasi
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QFormLayout
)
from PyQt6.QtCore import Qt

class PaymentDialog(QDialog):
    """
    Dialog pembayaran dengan validasi real-time
    
    Returns:
        accepted: bool - True jika user klik "PROSES BAYAR"
        uang_diterima: float - Nominal uang yang diterima
        kembalian: float - Kembalian yang harus dikembalikan
    """
    
    def __init__(self, total_belanja, parent=None):
        super().__init__(parent)
        
        self.total_belanja = total_belanja
        self.uang_diterima = 0
        self.kembalian = 0
        self.pembayaran_sukses = False
        
        self.setup_ui()
        
        # Window properties
        self.setWindowTitle("Pembayaran (Esc untuk Batal)")
        self.setFixedSize(400, 250)
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Label Total
        lbl_total = QLabel(f"Total Tagihan: Rp {int(self.total_belanja):,}")
        lbl_total.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: #d32f2f;
            padding: 10px;
            background-color: #1E1E1E;
            border-radius: 5px;
        """)
        lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_total)
        
        # Form Input
        form = QFormLayout()
        form.setVerticalSpacing(10)
        
        self.input_uang = QLineEdit()
        self.input_uang.setPlaceholderText("Masukkan nominal uang")
        self.input_uang.setStyleSheet("font-size: 14px; padding: 8px;")
        self.input_uang.returnPressed.connect(self.proses_bayar)
        self.input_uang.textChanged.connect(self.hitung_kembalian)
        
        form.addRow("Uang Diterima (Rp):", self.input_uang)
        layout.addLayout(form)
        
        # Label Kembalian
        self.lbl_kembalian = QLabel("Kembalian: Rp 0")
        self.lbl_kembalian.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            color: green;
            padding: 10px;
            background-color: #1E1E1E;
            border-radius: 5px;
        """)
        self.lbl_kembalian.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_kembalian)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.btn_batal = QPushButton("Batal (Esc)")
        self.btn_batal.setFixedHeight(40)
        self.btn_batal.setStyleSheet("""
            QPushButton {
                background-color: #424242;
                color: white;
                border: 2px solid #424242;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #616161; }
            QPushButton:focus { border: 2px solid #ffffff; }
        """)
        self.btn_batal.clicked.connect(self.reject)
        self.btn_batal.setAutoDefault(True)
        
        self.btn_proses = QPushButton("PROSES BAYAR (Enter)")
        self.btn_proses.setFixedHeight(40)
        self.btn_proses.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: 2px solid #2196F3;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #1976D2; }
            QPushButton:focus { border: 2px solid #ffffff; }
            QPushButton:disabled {
                background-color: #1a5a8a;
                border: 2px solid #1a5a8a;
            }
        """)
        self.btn_proses.clicked.connect(self.proses_bayar)
        self.btn_proses.setEnabled(False)
        self.btn_proses.setAutoDefault(True)
        self.btn_proses.setDefault(True)
        
        btn_layout.addWidget(self.btn_batal)
        btn_layout.addWidget(self.btn_proses)
        layout.addLayout(btn_layout)
        
        # Focus awal
        self.input_uang.setFocus()
    
    def hitung_kembalian(self):
        """Real-time calculation kembalian"""
        text = self.input_uang.text().strip().replace(".", "").replace(",", "")
        
        if text.isdigit():
            self.uang_diterima = int(text)
            self.kembalian = self.uang_diterima - self.total_belanja
            
            self.lbl_kembalian.setText(f"Kembalian: Rp {self.kembalian:,}")
            
            if self.kembalian >= 0:
                self.btn_proses.setEnabled(True)
                self.lbl_kembalian.setStyleSheet("""
                    font-size: 16px; 
                    font-weight: bold; 
                    color: #4CAF50;
                    padding: 10px;
                    background-color: #1E1E1E;
                    border-radius: 5px;
                """)
            else:
                self.btn_proses.setEnabled(False)
                self.lbl_kembalian.setStyleSheet("""
                    font-size: 16px; 
                    font-weight: bold; 
                    color: #F44336;
                    padding: 10px;
                    background-color: #1E1E1E;
                    border-radius: 5px;
                """)
        else:
            self.lbl_kembalian.setText("Kembalian: Rp 0")
            self.btn_proses.setEnabled(False)
    
    def proses_bayar(self):
        """Process payment if valid"""
        if self.btn_proses.isEnabled():
            self.pembayaran_sukses = True
            self.accept()
        else:
            self.input_uang.setFocus()
    
    def keyPressEvent(self, event):
        """Handle ESC key"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)