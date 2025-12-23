"""
Cyber Button Component
======================
Auto-sizing button dengan neon colors, no text terpotong

Usage:
    btn = CyberButton("Save Data", variant='success')
    btn.clicked.connect(self.save)
"""

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt
from src.ui.base.style_manager import StyleManager


class CyberButton(QPushButton):
    """
    Auto-sizing button dengan cyberpunk style
    
    Features:
    - Auto width based on text (no terpotong)
    - Consistent height per size
    - Neon color variants
    - Proper padding
    """
    
    def __init__(self, text: str = "", variant: str = 'default', 
                 size: str = 'medium', parent=None):
        """
        Args:
            text: Button text
            variant: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info'
            size: 'small' | 'medium' | 'large' | 'xlarge'
            parent: Parent widget
        """
        super().__init__(text, parent)
        
        self.variant = variant
        self.size = size
        
        self.setup_style()
        self.setup_size()
        
        # Cursor pointer
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def setup_style(self):
        """Apply cyberpunk style"""
        style = StyleManager.get_button_style(self.variant)
        self.setStyleSheet(style)
    
    def setup_size(self):
        """Auto-size button based on text"""
        # Height berdasarkan size
        heights = {
            'small': 35,
            'medium': 40,
            'large': 45,
            'xlarge': 60,
        }
        height = heights.get(self.size, 40)
        
        # Width: auto-fit text dengan padding
        self.adjustSize()
        text_width = self.width()
        
        # Minimum width + extra padding
        min_width = max(text_width + 40, 80)  # At least 80px
        
        self.setFixedHeight(height)
        self.setMinimumWidth(min_width)
    
    def setText(self, text: str):
        """Override setText to auto-resize"""
        super().setText(text)
        self.setup_size()
    
    def set_variant(self, variant: str):
        """Change button variant dynamically"""
        self.variant = variant
        self.setup_style()


# ========== CONVENIENCE FUNCTIONS ==========

def create_button(text: str, variant: str = 'default', 
                 size: str = 'medium', callback=None):
    """
    Quick create button with callback
    
    Usage:
        btn = create_button("Save", 'success', callback=self.save)
    """
    btn = CyberButton(text, variant, size)
    if callback:
        btn.clicked.connect(callback)
    return btn