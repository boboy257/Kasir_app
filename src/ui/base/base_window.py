"""
Base Window Class
=================
Parent class untuk semua window dengan fitur:
- Auto keyboard navigation setup
- Standardized dialogs
- Common utilities
- Error handling
"""

from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtCore import Qt, QEvent

class BaseWindow(QMainWindow):
    """
    Base class untuk semua window
    
    Features:
    - Keyboard navigation support
    - Standardized dialogs
    - Common utilities
    
    Usage:
        class MyWindow(BaseWindow):
            def __init__(self):
                super().__init__()
                self.setup_ui()
                self.setup_navigation()
    """
    
    def __init__(self):
        super().__init__()
        
        # Current user (akan di-set dari main window)
        self.current_user = None
        
        # Navigation map untuk keyboard shortcuts
        self._navigation_map = {}
        
        # Install event filter untuk keyboard handling
        self.installEventFilter(self)
    
    def set_current_user(self, username):
        """Set current user (dipanggil dari main window)"""
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
            True jika user klik Yes, False jika No
        """
        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
    
    # ========== KEYBOARD NAVIGATION ==========
    
    def register_navigation(self, widget, navigation_dict: dict):
        """
        Register keyboard navigation untuk widget
        
        Args:
            widget: Widget yang akan di-register
            navigation_dict: Dict dengan key = Qt.Key, value = target widget/function
            
        Example:
            self.register_navigation(self.input_username, {
                Qt.Key.Key_Down: self.input_password,
                Qt.Key.Key_Return: self.input_password,
            })
        """
        widget.installEventFilter(self)
        self._navigation_map[widget] = navigation_dict
    
    def eventFilter(self, obj, event):
        """Handle keyboard navigation"""
        if event.type() == QEvent.Type.KeyPress:
            
            # Global ESC handler
            if event.key() == Qt.Key.Key_Escape:
                return self.handle_escape()
            
            # Widget-specific navigation
            if obj in self._navigation_map:
                nav_dict = self._navigation_map[obj]
                
                if event.key() in nav_dict:
                    target = nav_dict[event.key()]
                    
                    if callable(target):
                        # Jika target adalah function
                        target()
                    elif target is not None:
                        # Jika target adalah widget
                        target.setFocus()
                        # Auto-select text untuk LineEdit
                        if hasattr(target, 'selectAll'):
                            target.selectAll()
                    
                    return True
        
        return super().eventFilter(obj, event)
    
    def handle_escape(self) -> bool:
        """
        Handle ESC key press
        Override ini di subclass jika perlu custom behavior
        
        Returns:
            True jika event handled
        """
        self.close()
        return True
    
    # ========== HELPER UTILITIES ==========
    
    def focus_table_first_row(self, table):
        """Helper: Focus table & select first row"""
        if table.rowCount() > 0:
            table.setFocus()
            table.selectRow(0)
    
    def focus_table_last_row(self, table):
        """Helper: Focus table & select last row"""
        if table.rowCount() > 0:
            table.setFocus()
            table.selectRow(table.rowCount() - 1)
    
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