"""
Cyber Card Component
====================
Dark card dengan neon border untuk dashboard/panels

Usage:
    card = CyberCard(variant='neon')
    layout = QVBoxLayout(card)
    layout.addWidget(QLabel("Content"))
"""

from PyQt6.QtWidgets import QFrame
from src.ui.base.style_manager import StyleManager


class CyberCard(QFrame):
    """
    Dark card dengan cyberpunk style
    
    Variants:
    - default: Standard dark card
    - elevated: Elevated surface
    - neon: Neon cyan border
    """
    
    def __init__(self, variant: str = 'default', parent=None):
        """
        Args:
            variant: 'default' | 'elevated' | 'neon'
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.variant = variant
        self.setup_style()
    
    def setup_style(self):
        """Apply card style"""
        style = StyleManager.get_card_style(self.variant)
        self.setStyleSheet(style)
    
    def set_variant(self, variant: str):
        """Change card variant dynamically"""
        self.variant = variant
        self.setup_style()