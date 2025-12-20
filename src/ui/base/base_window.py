"""
Base Window Class - UPDATED for SmartNavigation
================================================
Parent class dengan SmartNavigationMixin integrated
"""

from PyQt6.QtWidgets import QMainWindow, QMessageBox
from src.ui.base.smart_navigation_mixin import SmartNavigationMixin
from PyQt6.QtGui import QShortcut, QKeySequence


class BaseWindow(QMainWindow, SmartNavigationMixin):
    """
    Base class untuk semua window dengan smart keyboard navigation
    
    Features:
    - Smart keyboard navigation (circular, memory, grid)
    - Standardized dialogs
    - Common utilities
    
    Usage:
        class MyWindow(BaseWindow):
            def __init__(self):
                super().__init__()
                self.setup_ui()
                self.setup_navigation()  # Setup navigation di sini
    """
    
    def __init__(self):
        super().__init__()
        
        # Setup smart navigation system
        self.setup_keyboard_navigation()
        
        # Current user (set by main window)
        self.current_user = None
    
    # ========== USER MANAGEMENT ==========
    
    def set_current_user(self, username):
        """Set current user"""
        self.current_user = username
    
    # ========== STANDARDIZED DIALOGS ==========
    
    def show_error(self, title: str, message: str):
        """Error dialog"""
        QMessageBox.critical(self, title, message)
    
    def show_success(self, title: str, message: str):
        """Success dialog"""
        QMessageBox.information(self, title, message)
    
    def show_warning(self, title: str, message: str):
        """Warning dialog"""
        QMessageBox.warning(self, title, message)
    
    def confirm_action(self, title: str, message: str) -> bool:
        """
        Confirmation dialog
        Returns: True if Yes, False if No
        """
        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
    
    # ========== HELPER UTILITIES ==========
    
    def clear_form(self, *widgets):
        """Clear multiple input widgets"""
        for widget in widgets:
            if hasattr(widget, 'clear'):
                widget.clear()
            elif hasattr(widget, 'setCurrentIndex'):
                widget.setCurrentIndex(0)
    
    def enable_widgets(self, enabled: bool, *widgets):
        """Enable/disable multiple widgets"""
        for widget in widgets:
            widget.setEnabled(enabled)
    
    # ========== OVERRIDE METHODS ==========
    
    def handle_escape(self) -> bool:
        """
        Handle ESC key (from SmartNavigationMixin)
        Override untuk custom behavior
        """
        self.close()
        return True
    
    def setup_help_overlay(self, shortcuts: dict):
        """Setup F1 help overlay"""
        from src.ui.widgets.help_overlay import HelpOverlay
        
        self.help_overlay = HelpOverlay(self)
        self.help_overlay.set_shortcuts(shortcuts)
        
        # ✅ Register F1 dengan QShortcut (bukan register_shortcut)
        self.help_shortcut = QShortcut(QKeySequence("F1"), self)
        self.help_shortcut.activated.connect(self.help_overlay.toggle)