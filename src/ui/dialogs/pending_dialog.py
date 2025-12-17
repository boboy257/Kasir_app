"""
Pending Transaction Dialog - FIXED NAVIGATION
==============================================
✅ Full keyboard navigation untuk 3 tombol
✅ Tab untuk pindah antar tombol
✅ Arrow keys untuk navigasi
✅ Enter untuk execute
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QMessageBox
)
from PyQt6.QtCore import Qt, QEvent

class PendingDialog(QDialog):
    """
    Dialog pilih transaksi pending - FULL KEYBOARD SUPPORT
    
    KEYBOARD SHORTCUTS:
    - Enter (on list) = Recall
    - Delete (on list) = Hapus
    - Tab = Next button
    - Shift+Tab = Previous button
    - Arrow Left/Right = Navigate buttons
    - Arrow Up/Down = Navigate list
    - ESC = Cancel
    """
    
    def __init__(self, daftar_pending, parent=None):
        super().__init__(parent)
        
        self.daftar_pending = daftar_pending
        self.selected_index = None
        
        self.setup_ui()
        self.setup_keyboard_navigation()  # ✅ NEW!
        
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
            QListWidget:focus {
                border: 2px solid #2196F3;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                border: 2px solid transparent;
            }
            QPushButton:focus {
                border: 2px solid #2196F3;
                background-color: rgba(33, 150, 243, 0.1);
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
        layout.addWidget(self.list_widget)
        
        # Info
        lbl_info = QLabel(
            "💡 Keyboard: Enter=Recall | Delete=Hapus | Tab=Pindah Tombol | ESC=Batal"
        )
        lbl_info.setStyleSheet("font-size: 10px; color: #666; font-style: italic;")
        layout.addWidget(lbl_info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_recall = QPushButton("✅ Recall (Enter)")
        self.btn_recall.setObjectName("btnRecall")
        self.btn_recall.setStyleSheet("""
            QPushButton { background-color: #4CAF50; color: white; }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.btn_recall.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_recall.clicked.connect(self.recall_selected)
        
        self.btn_hapus = QPushButton("🗑️ Hapus (Delete)")
        self.btn_hapus.setObjectName("btnHapus")
        self.btn_hapus.setStyleSheet("""
            QPushButton { background-color: #f44336; color: white; }
            QPushButton:hover { background-color: #d32f2f; }
        """)
        self.btn_hapus.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_hapus.clicked.connect(self.hapus_selected)
        
        self.btn_batal = QPushButton("❌ Batal (ESC)")
        self.btn_batal.setObjectName("btnBatal")
        self.btn_batal.setStyleSheet("""
            QPushButton { background-color: #757575; color: white; }
            QPushButton:hover { background-color: #616161; }
        """)
        self.btn_batal.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_batal.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_recall)
        btn_layout.addWidget(self.btn_hapus)
        btn_layout.addWidget(self.btn_batal)
        layout.addLayout(btn_layout)
        
        # Initial focus
        self.list_widget.setFocus()
        if len(self.daftar_pending) > 0:
            self.list_widget.setCurrentRow(0)
    
    def setup_keyboard_navigation(self):
        """
        ✅ SETUP KEYBOARD NAVIGATION
        Ini yang PENTING untuk navigasi 3 tombol!
        """
        # Install event filter pada semua widget penting
        self.list_widget.installEventFilter(self)
        self.btn_recall.installEventFilter(self)
        self.btn_hapus.installEventFilter(self)
        self.btn_batal.installEventFilter(self)
    
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
        """
        ✅ KEYBOARD NAVIGATION HANDLER
        Ini yang handle semua navigasi keyboard!
        """
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            
            # ========== LIST WIDGET ==========
            if obj == self.list_widget:
                # Enter = Recall
                if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self.recall_selected()
                    return True
                
                # Delete = Hapus
                if key == Qt.Key.Key_Delete:
                    self.hapus_selected()
                    return True
                
                # Down at last item = Jump to buttons
                if key == Qt.Key.Key_Down:
                    if self.list_widget.currentRow() == self.list_widget.count() - 1:
                        self.btn_recall.setFocus()
                        return True
                
                # Tab = Jump to first button
                if key == Qt.Key.Key_Tab:
                    self.btn_recall.setFocus()
                    return True
            
            # ========== BUTTON: RECALL ==========
            elif obj == self.btn_recall:
                # Enter/Space = Execute
                if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
                    self.recall_selected()
                    return True
                
                # Right/Tab = Next button
                if key in (Qt.Key.Key_Right, Qt.Key.Key_Tab):
                    self.btn_hapus.setFocus()
                    return True
                
                # Up = Back to list
                if key == Qt.Key.Key_Up:
                    self.list_widget.setFocus()
                    return True
                
                # Left = Last button (circular)
                if key == Qt.Key.Key_Left:
                    self.btn_batal.setFocus()
                    return True
            
            # ========== BUTTON: HAPUS ==========
            elif obj == self.btn_hapus:
                # Enter/Space = Execute
                if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
                    self.hapus_selected()
                    return True
                
                # Right/Tab = Next button
                if key in (Qt.Key.Key_Right, Qt.Key.Key_Tab):
                    self.btn_batal.setFocus()
                    return True
                
                # Left = Previous button
                if key == Qt.Key.Key_Left:
                    self.btn_recall.setFocus()
                    return True
                
                # Up = Back to list
                if key == Qt.Key.Key_Up:
                    self.list_widget.setFocus()
                    return True
            
            # ========== BUTTON: BATAL ==========
            elif obj == self.btn_batal:
                # Enter/Space = Execute
                if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
                    self.reject()
                    return True
                
                # Right/Tab = First button (circular)
                if key in (Qt.Key.Key_Right, Qt.Key.Key_Tab):
                    self.btn_recall.setFocus()
                    return True
                
                # Left = Previous button
                if key == Qt.Key.Key_Left:
                    self.btn_hapus.setFocus()
                    return True
                
                # Up = Back to list
                if key == Qt.Key.Key_Up:
                    self.list_widget.setFocus()
                    return True
        
        # Pass event ke parent
        return super().eventFilter(obj, event)
    
    def keyPressEvent(self, event):
        """Handle global ESC key"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)