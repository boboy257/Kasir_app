"""
Pending Transaction Dialog
===========================
Dialog untuk recall atau hapus transaksi pending
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QMessageBox
)
from PyQt6.QtCore import Qt, QEvent

class PendingDialog(QDialog):
    """
    Dialog pilih transaksi pending
    
    Returns:
        result code:
            - 1 (Accepted): User klik Recall
            - 2 (Custom): User klik Hapus
            - 0 (Rejected): User klik Batal
        selected_index: int - Index transaksi yang dipilih
    """
    
    def __init__(self, daftar_pending, parent=None):
        super().__init__(parent)
        
        self.daftar_pending = daftar_pending
        self.selected_index = None
        
        self.setup_ui()
        
        # Window properties
        self.setWindowTitle("Pilih Transaksi Pending")
        self.setFixedSize(500, 400)
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Styling
        self.setStyleSheet("""
            QDialog { background-color: #f5f5f5; }
            QLabel { color: #333; }
            QListWidget {
                background-color: white;
                color: #000000;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 12px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        
        # Header
        lbl_header = QLabel(f"📋 Daftar Transaksi Pending ({len(self.daftar_pending)})")
        lbl_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #1976D2; margin-bottom: 10px;")
        layout.addWidget(lbl_header)
        
        # List Pending
        self.list_widget = QListWidget()
        
        for idx, pending in enumerate(self.daftar_pending):
            timestamp = pending['timestamp']
            total = pending['total']
            note = pending.get('note', '')
            item_count = len(pending['keranjang'])
            
            if note:
                text = f"#{idx+1} - {timestamp} - Rp {int(total):,}\n      📝 {note} ({item_count} items)"
            else:
                text = f"#{idx+1} - {timestamp} - Rp {int(total):,} ({item_count} items)"
            
            self.list_widget.addItem(text)
        
        self.list_widget.itemDoubleClicked.connect(self.recall_selected)
        self.list_widget.installEventFilter(self)
        layout.addWidget(self.list_widget)
        
        # Info
        lbl_info = QLabel("💡 Double-click atau pilih lalu klik Recall")
        lbl_info.setStyleSheet("font-size: 10px; color: #666; font-style: italic;")
        layout.addWidget(lbl_info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_recall = QPushButton("✅ Recall")
        self.btn_recall.setObjectName("btnRecall")
        self.btn_recall.setStyleSheet("background-color: #4CAF50; color: white; border: none;")
        self.btn_recall.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_recall.clicked.connect(self.recall_selected)
        self.btn_recall.installEventFilter(self)
        
        self.btn_hapus = QPushButton("🗑️ Hapus")
        self.btn_hapus.setObjectName("btnHapus")
        self.btn_hapus.setStyleSheet("background-color: #f44336; color: white; border: none;")
        self.btn_hapus.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_hapus.clicked.connect(self.hapus_selected)
        self.btn_hapus.installEventFilter(self)
        
        self.btn_batal = QPushButton("❌ Batal")
        self.btn_batal.setObjectName("btnBatal")
        self.btn_batal.setStyleSheet("background-color: #757575; color: white; border: none;")
        self.btn_batal.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_batal.clicked.connect(self.reject)
        self.btn_batal.installEventFilter(self)
        
        btn_layout.addWidget(self.btn_recall)
        btn_layout.addWidget(self.btn_hapus)
        btn_layout.addWidget(self.btn_batal)
        layout.addLayout(btn_layout)
        
        # Initial focus
        self.list_widget.setFocus()
        if len(self.daftar_pending) > 0:
            self.list_widget.setCurrentRow(0)
    
    def recall_selected(self):
        """Recall transaksi yang dipilih"""
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            self.selected_index = current_row
            self.accept()
        else:
            QMessageBox.warning(self, "Pilih Transaksi", "Pilih transaksi yang ingin di-recall")
    
    def hapus_selected(self):
        """Hapus transaksi yang dipilih"""
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(
                self, "Hapus Pending", 
                "Yakin hapus transaksi pending ini?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.selected_index = current_row
                self.done(2)  # Custom return code untuk hapus
        else:
            QMessageBox.warning(self, "Pilih Transaksi", "Pilih transaksi yang ingin dihapus")
    
    def eventFilter(self, obj, event):
        """Handle keyboard navigation"""
        if event.type() == QEvent.Type.KeyPress:
            # List: Enter = recall, Delete = hapus
            if obj == self.list_widget:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self.recall_selected()
                    return True
                elif event.key() == Qt.Key.Key_Delete:
                    self.hapus_selected()
                    return True
                elif event.key() == Qt.Key.Key_Down:
                    if self.list_widget.currentRow() == self.list_widget.count() - 1:
                        self.btn_recall.setFocus()
                        return True
            
            # Tombol Recall
            elif obj == self.btn_recall:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self.recall_selected()
                    return True
                elif event.key() == Qt.Key.Key_Right:
                    self.btn_hapus.setFocus()
                    return True
                elif event.key() == Qt.Key.Key_Up:
                    self.list_widget.setFocus()
                    return True
            
            # Tombol Hapus
            elif obj == self.btn_hapus:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self.hapus_selected()
                    return True
                elif event.key() == Qt.Key.Key_Left:
                    self.btn_recall.setFocus()
                    return True
                elif event.key() == Qt.Key.Key_Right:
                    self.btn_batal.setFocus()
                    return True
                elif event.key() == Qt.Key.Key_Up:
                    self.list_widget.setFocus()
                    return True
            
            # Tombol Batal
            elif obj == self.btn_batal:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self.reject()
                    return True
                elif event.key() == Qt.Key.Key_Left:
                    self.btn_hapus.setFocus()
                    return True
                elif event.key() == Qt.Key.Key_Up:
                    self.list_widget.setFocus()
                    return True
        
        return super().eventFilter(obj, event)
    
    def keyPressEvent(self, event):
        """Handle ESC key"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)