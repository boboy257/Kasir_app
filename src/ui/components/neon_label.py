"""
Neon Label Component
====================
Colored text dengan neon colors

Usage:
    lbl = NeonLabel("Total: Rp 100.000", color='cyan', size='large')
"""

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from src.ui.base.design_tokens import CyberpunkColors, CyberpunkTypography


class NeonLabel(QLabel):
    """
    Label dengan neon colors
    
    Colors: cyan, pink, green, orange, purple, white
    Sizes: small, medium, large, xlarge
    """
    
    def __init__(self, text: str = "", color: str = 'cyan', 
                 size: str = 'medium', bold: bool = False, parent=None):
        """
        Args:
            text: Label text
            color: 'cyan' | 'pink' | 'green' | 'orange' | 'purple' | 'white'
            size: 'small' | 'medium' | 'large' | 'xlarge'
            bold: Bold text
            parent: Parent widget
        """
        super().__init__(text, parent)
        
        self.color = color
        self.size = size
        self.bold = bold
        
        self.setup_style()
    
    def setup_style(self):
        """Apply neon style"""
        # Color mapping
        colors = {
            'cyan': CyberpunkColors.NEON_CYAN,
            'pink': CyberpunkColors.NEON_PINK,
            'green': CyberpunkColors.NEON_GREEN,
            'orange': CyberpunkColors.NEON_ORANGE,
            'purple': CyberpunkColors.NEON_PURPLE,
            'white': CyberpunkColors.TEXT_PRIMARY,
            'gray': CyberpunkColors.TEXT_SECONDARY,
        }
        
        # Size mapping
        sizes = {
            'small': CyberpunkTypography.SIZE_S,
            'medium': CyberpunkTypography.SIZE_M,
            'large': CyberpunkTypography.SIZE_L,
            'xlarge': CyberpunkTypography.SIZE_XL,
            'xxlarge': CyberpunkTypography.SIZE_XXL,
        }
        
        color_hex = colors.get(self.color, CyberpunkColors.TEXT_PRIMARY)
        font_size = sizes.get(self.size, CyberpunkTypography.SIZE_M)
        font_weight = 'bold' if self.bold else 'normal'
        
        self.setStyleSheet(f"""
            QLabel {{
                color: {color_hex};
                font-size: {font_size}px;
                font-weight: {font_weight};
                background: transparent;
                border: none;
            }}
        """)