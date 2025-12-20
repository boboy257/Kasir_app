"""
Multi Payment Dialog
====================
Dialog untuk input pembayaran dengan multiple payment methods
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QFormLayout, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator


class MultiPaymentDialog(QDialog):
    """
    Dialog multi-payment dengan 5 metode pembayaran
    
    Returns:
        accepted: bool
        payments: dict - {'cash': 50000, 'debit': 30000, ...}
        kembalian: float
    """
    
    PAYMENT_METHODS = {
        'cash': 'Tunai',
        'debit': 'Kartu Debit',
        'credit': 'Kartu Kredit',
        'ewallet': 'E-Wallet',
        'transfer': 'Transfer Bank'
    }
    
    def __init__(self, total_belanja, parent=None):
        super().__init__(parent)
        
        self.total_belanja = total_belanja
        self.payments = {}
        self.kembalian = 0
        
        self.setup_ui()
        self.setup_navigation()
        
        self.setWindowTitle("Multi-Payment")
        self.setFixedSize(500, 600)
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        lbl_total = QLabel(f"Total Tagihan: Rp {int(self.total_belanja):,}")
        lbl_total.setStyleSheet("font-size: 20px; font-weight: bold; color: #F44336;")
        lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_total)
        
        self.lbl_terbayar = QLabel("Terbayar: Rp 0")
        self.lbl_terbayar.setStyleSheet("font-size: 16px; color: #2196F3;")
        self.lbl_terbayar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_terbayar)
        
        self.lbl_sisa = QLabel(f"Kurang: Rp {int(self.total_belanja):,}")
        self.lbl_sisa.setStyleSheet("font-size: 16px; color: #FF9800;")
        self.lbl_sisa.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_sisa)
        
        layout.addSpacing(20)
        
        # Payment inputs (SIMPLE!)
        self.inputs = {}
        validator = QDoubleValidator(0.0, 999999999.0, 0)
        
        for method_key, method_name in self.PAYMENT_METHODS.items():
            row = QHBoxLayout()
            
            lbl = QLabel(f"{method_name}:")
            lbl.setFixedWidth(130)
            
            inp = QLineEdit()
            inp.setPlaceholderText("Masukkan nominal...")
            inp.setValidator(validator)
            inp.textChanged.connect(self.calculate_payments)
            
            self.inputs[method_key] = inp
            
            row.addWidget(lbl)
            row.addWidget(inp)
            layout.addLayout(row)
        
        layout.addSpacing(20)
        
        # Kembalian
        self.lbl_kembalian = QLabel("Kembalian: Rp 0")
        self.lbl_kembalian.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50;")
        self.lbl_kembalian.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_kembalian)
        
        layout.addSpacing(10)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_batal = QPushButton("Batal (Esc)")
        self.btn_batal.setFixedHeight(45)
        self.btn_batal.clicked.connect(self.reject)
        
        self.btn_proses = QPushButton("PROSES BAYAR (Enter)")
        self.btn_proses.setFixedHeight(45)
        self.btn_proses.clicked.connect(self.proses_bayar)
        self.btn_proses.setEnabled(False)
        
        from src.ui.base.style_manager import StyleManager
        style = StyleManager()
        self.btn_proses.setStyleSheet(style.get_button_style('success'))
        
        btn_layout.addWidget(self.btn_batal)
        btn_layout.addWidget(self.btn_proses)
        layout.addLayout(btn_layout)
        
        # Info
        lbl_info = QLabel("💡 Isi minimal 1 metode | Total harus pas atau lebih")
        lbl_info.setStyleSheet("color: #666; font-size: 10px;")
        lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_info)
        
        self.inputs['cash'].setFocus()
    
    def setup_navigation(self):
        """Keyboard navigation untuk payment inputs"""
        methods = list(self.PAYMENT_METHODS.keys())
        
        for i, method in enumerate(methods):
            input_field = self.inputs[method]
            
            nav = {}
            
            # Down navigation
            if i < len(methods) - 1:
                nav[Qt.Key.Key_Down] = self.inputs[methods[i + 1]]
            else:
                nav[Qt.Key.Key_Down] = self.btn_proses
            
            # Up navigation
            if i > 0:
                nav[Qt.Key.Key_Up] = self.inputs[methods[i - 1]]
            
            # Enter
            if i < len(methods) - 1:
                nav[Qt.Key.Key_Return] = self.inputs[methods[i + 1]]
            else:
                nav[Qt.Key.Key_Return] = self.btn_proses
            
            # Register navigation
            for key, target in nav.items():
                input_field.installEventFilter(self)
                # Manual eventFilter akan handle ini
    
    def eventFilter(self, obj, event):
        """Handle keyboard navigation"""
        if event.type() == event.Type.KeyPress:
            key = event.key()
            
            # Find current input
            for i, (method, input_field) in enumerate(self.inputs.items()):
                if obj == input_field:
                    methods = list(self.inputs.keys())
                    
                    if key == Qt.Key.Key_Down:
                        if i < len(methods) - 1:
                            self.inputs[methods[i + 1]].setFocus()
                        else:
                            self.btn_proses.setFocus()
                        return True
                    
                    elif key == Qt.Key.Key_Up:
                        if i > 0:
                            self.inputs[methods[i - 1]].setFocus()
                        return True
                    
                    elif key == Qt.Key.Key_Return:
                        if i < len(methods) - 1:
                            self.inputs[methods[i + 1]].setFocus()
                        else:
                            if self.btn_proses.isEnabled():
                                self.proses_bayar()
                        return True
        
        return super().eventFilter(obj, event)
    
    def calculate_payments(self):
        """Calculate total payments & kembalian"""
        total_dibayar = 0
        self.payments = {}
        
        for method, input_field in self.inputs.items():
            text = input_field.text().strip()
            if text and text.replace('.', '').isdigit():
                amount = float(text)
                if amount > 0:
                    self.payments[method] = amount
                    total_dibayar += amount
        
        # Update labels
        self.lbl_terbayar.setText(f"Terbayar: Rp {int(total_dibayar):,}")
        
        sisa = self.total_belanja - total_dibayar
        
        if sisa > 0:
            self.lbl_sisa.setText(f"Kurang: Rp {int(sisa):,}")
            self.lbl_sisa.setStyleSheet("font-size: 16px; color: #FF9800;")
            self.lbl_kembalian.setText("Kembalian: Rp 0")
            self.lbl_kembalian.setStyleSheet("""
                font-size: 18px; font-weight: bold; color: #666;
                padding: 15px; background-color: #1E1E1E; border-radius: 8px;
            """)
            self.btn_proses.setEnabled(False)
        
        elif sisa < 0:
            self.kembalian = abs(sisa)
            self.lbl_sisa.setText("Lunas ✓")
            self.lbl_sisa.setStyleSheet("font-size: 16px; color: #4CAF50;")
            self.lbl_kembalian.setText(f"Kembalian: Rp {int(self.kembalian):,}")
            self.lbl_kembalian.setStyleSheet("""
                font-size: 18px; font-weight: bold; color: #4CAF50;
                padding: 15px; background-color: #1E1E1E; border-radius: 8px;
            """)
            self.btn_proses.setEnabled(True)
        
        else:  # Pas
            self.kembalian = 0
            self.lbl_sisa.setText("Lunas ✓")
            self.lbl_sisa.setStyleSheet("font-size: 16px; color: #4CAF50;")
            self.lbl_kembalian.setText("Pembayaran Pas ✓")
            self.lbl_kembalian.setStyleSheet("""
                font-size: 18px; font-weight: bold; color: #4CAF50;
                padding: 15px; background-color: #1E1E1E; border-radius: 8px;
            """)
            self.btn_proses.setEnabled(True)
    
    def proses_bayar(self):
        """Process payment"""
        if self.btn_proses.isEnabled() and self.payments:
            self.accept()
    
    def keyPressEvent(self, event):
        """Handle ESC key"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)