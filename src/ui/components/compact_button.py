"""
Compact Button System - PROFESSIONAL
=====================================
No bloat, no text terpotong, perfect sizing
"""

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from src.ui.base.style_manager import StyleManager


class CompactButton(QPushButton):
    """
    Compact professional button
    
    Design rules:
    - Height: 36px (compact, not bloated)
    - Width: Auto-fit text + 20px padding
    - Min width: 70px
    - Max width: 150px (prevent bloat)
    - Font: 12px (readable, not huge)
    - Icon optional (keep short)
    """
    
    def __init__(self, text: str = "", variant: str = 'default', 
                 icon: str = "", parent=None):
        """
        Args:
            text: Short text (e.g. "Cari", "Simpan")
            variant: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info'
            icon: Optional emoji icon (1 char only)
            parent: Parent widget
        """
        # Combine icon + text
        display_text = f"{icon} {text}".strip() if icon else text
        super().__init__(display_text, parent)
        
        self.variant = variant
        self.setup_style()
        self.setup_size()
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def setup_style(self):
        """Apply compact style"""
        style = StyleManager.get_button_style(self.variant)
        
        # Override with compact settings
        compact_style = style + """
            QPushButton {
                padding: 8px 16px;
                font-size: 12px;
                min-height: 36px;
                max-height: 36px;
            }
        """
        self.setStyleSheet(compact_style)
    
    def setup_size(self):
        """Smart auto-sizing"""
        # Get text width
        font = QFont("Segoe UI", 12)
        metrics = self.fontMetrics()
        text_width = metrics.horizontalAdvance(self.text())
        
        # Calculate button width: text + padding + borders
        button_width = text_width + 40  # 20px padding each side + borders
        
        # Apply constraints
        button_width = max(button_width, 70)   # Min 70px
        button_width = min(button_width, 150)  # Max 150px
        
        self.setFixedHeight(36)
        self.setFixedWidth(button_width)
    
    def setText(self, text: str):
        """Override setText to auto-resize"""
        super().setText(text)
        self.setup_size()
    
    def set_variant(self, variant: str):
        """Change variant dynamically"""
        self.variant = variant
        self.setup_style()


class IconButton(CompactButton):
    """Icon-only button (square, 36x36px)"""
    
    def __init__(self, icon: str, variant: str = 'default', 
                 tooltip: str = "", parent=None):
        super().__init__(icon, variant, "", parent)
        self.setFixedSize(36, 36)
        if tooltip:
            self.setToolTip(tooltip)


class ActionButton(CompactButton):
    """Action button with F-key hint in tooltip"""
    
    def __init__(self, text: str, fkey: str = "", variant: str = 'default',
                 icon: str = "", parent=None):
        super().__init__(text, variant, icon, parent)
        
        if fkey:
            tooltip = f"{text} ({fkey})"
            self.setToolTip(tooltip)


# ========== CONVENIENCE FUNCTIONS ==========

def create_action_button(text: str, fkey: str, variant: str, 
                         icon: str = "", callback=None):
    """
    Quick create action button
    
    Usage:
        btn = create_action_button("Cari", "F4", 'primary', '🔍', self.search)
    """
    btn = ActionButton(text, fkey, variant, icon)
    if callback:
        btn.clicked.connect(callback)
    return btn


def create_toolbar_buttons(buttons_config: list):
    """
    Create multiple buttons from config
    
    Usage:
        buttons = create_toolbar_buttons([
            ("Cari", "F4", 'primary', '🔍', self.search),
            ("Hapus", "Del", 'danger', '🗑️', self.delete),
        ])
    
    Returns:
        List of CompactButton
    """
    buttons = []
    for config in buttons_config:
        text, fkey, variant, icon, callback = config
        btn = create_action_button(text, fkey, variant, icon, callback)
        buttons.append(btn)
    return buttons