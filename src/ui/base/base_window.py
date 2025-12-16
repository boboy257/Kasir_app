"""
Base Window Class (UPDATED)
============================
Parent class dengan KeyboardMixin integrated

Changes:
- ✅ Multiple inheritance: QMainWindow + KeyboardMixin
- ✅ Simplified initialization
- ✅ Remove duplicate eventFilter
- ✅ Keep standardized dialogs & utilities
"""

from PyQt6.QtWidgets import QMainWindow, QMessageBox
from src.ui.base.keyboard_mixin import KeyboardMixin


class BaseWindow(QMainWindow, KeyboardMixin):
    """
    Base class untuk semua window dengan keyboard navigation
    
    Features:
    - Auto keyboard navigation setup
    - Standardized dialogs
    - Common utilities
    - Consistent ESC handling
    
    Usage:
        class MyWindow(BaseWindow):
            def __init__(self):
                super().__init__()
                self.setup_ui()
                self.setup_navigation()
            
            def setup_navigation(self):
                # Basic navigation
                self.register_navigation(self.input1, {
                    Qt.Key.Key_Down: self.input2,
                    Qt.Key.Key_Return: self.save_button
                })
                
                # Table shortcuts
                self.register_table_callbacks(self.table, {
                    'edit': self.edit_row,
                    'delete': self.delete_row,
                    'focus_up': self.search_input
                })
                
                # Custom shortcuts
                self.register_shortcut(Qt.Key.Key_F3, self.custom_action)
    """
    
    def __init__(self):
        super().__init__()
        
        # Setup keyboard navigation system
        self.setup_keyboard_navigation()
        
        # Current user (set by main window)
        self.current_user = None
    
    # ========== USER MANAGEMENT ==========
    
    def set_current_user(self, username):
        """Set current user (called from main window)"""
        self.current_user = username
    
    # ========== STANDARDIZED DIALOGS ==========
    
    def show_error(self, title: str, message: str):
        """Standardized error dialog"""
        QMessageBox.critical(self, title, message)
    
    def show_success(self, title: str, message: str):
        """Standardized success dialog"""
        QMessageBox.information(self, title, message)
    
    def show_warning(self, title: str, message: str):
        """Standardized warning dialog"""
        QMessageBox.warning(self, title, message)
    
    def confirm_action(self, title: str, message: str) -> bool:
        """
        Standardized confirmation dialog
        
        Returns:
            True if user clicked Yes, False if No
        """
        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
    
    # ========== HELPER UTILITIES ==========
    
    def clear_form(self, *widgets):
        """Helper: Clear multiple input widgets"""
        for widget in widgets:
            if hasattr(widget, 'clear'):
                widget.clear()
            elif hasattr(widget, 'setCurrentIndex'):
                widget.setCurrentIndex(0)
    
    def enable_widgets(self, enabled: bool, *widgets):
        """Helper: Enable/disable multiple widgets"""
        for widget in widgets:
            widget.setEnabled(enabled)
    
    # ========== OVERRIDE METHODS ==========
    
    def handle_escape(self) -> bool:
        """
        Override ESC handling (from KeyboardMixin)
        Default: Close window
        
        Override ini untuk custom behavior (e.g., konfirmasi jika ada perubahan)
        """
        self.close()
        return True