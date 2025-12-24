"""
Style Manager - CYBERPUNK EDITION
==================================
Centralized style management dengan Cyberpunk design tokens
"""

from pathlib import Path
from PyQt6.QtWidgets import QApplication
from src.ui.base.design_tokens import (
    CyberpunkColors, CyberpunkTypography, CyberpunkSpacing,
    CyberpunkSizes, get_color
)


class ButtonSize:
    """Standard button sizes"""
    SMALL = 35
    MEDIUM = 40
    LARGE = 45
    XLARGE = 60
    MIN_WIDTH_NARROW = 80
    MIN_WIDTH_NORMAL = 120
    MIN_WIDTH_WIDE = 150
    MIN_WIDTH_FULL = 200


class StyleManager:
    """
    Singleton class untuk manage styles - CYBERPUNK EDITION
    
    Features:
    - Load theme dari QSS file
    - Get colors by name (Cyberpunk palette)
    - Get component styles by variant (neon colors, no glow in CSS)
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.styles_path = Path(__file__).parent.parent.parent.parent / "resources" / "styles"
            self.current_theme = "dark"
            self.initialized = True
    
    def load_theme(self, theme: str = "dark") -> bool:
        """Load theme dari QSS file"""
        qss_file = self.styles_path / f"{theme}_theme.qss"
        
        if qss_file.exists():
            try:
                with open(qss_file, 'r', encoding='utf-8') as f:
                    stylesheet = f.read()
                
                QApplication.instance().setStyleSheet(stylesheet)
                self.current_theme = theme
                return True
            except Exception as e:
                print(f"Error loading theme: {e}")
                return False
        else:
            print(f"Theme file not found: {qss_file}")
            return False
    
    # ========== COLOR PALETTE (CYBERPUNK) ==========
    
    @staticmethod
    def get_color(name: str) -> str:
        """Get color by name - uses design tokens"""
        return get_color(name)
    
    # ========== BUTTON STYLES (CYBERPUNK) ==========
    
    @staticmethod
    def get_button_style(variant: str = 'default') -> str:
        """
        Get button style - CYBERPUNK EDITION dengan neon colors
        
        Variants:
        - default: Neutral gray
        - primary: Neon Cyan (main actions)
        - success: Neon Green (save, confirm)
        - warning: Neon Orange (edit, pending)
        - danger: Neon Pink (delete)
        - info: Neon Purple (info)
        """
        
        styles = {
            'default': f"""
                QPushButton {{ 
                    background-color: {CyberpunkColors.BG_ELEVATED}; 
                    color: {CyberpunkColors.TEXT_PRIMARY}; 
                    border: 2px solid {CyberpunkColors.BORDER_DEFAULT}; 
                    padding: 10px 20px; 
                    border-radius: {CyberpunkSizes.RADIUS_MD}px; 
                    font-weight: bold;
                    font-size: {CyberpunkTypography.SIZE_M}px;
                }}
                QPushButton:hover {{ 
                    background-color: {CyberpunkColors.BG_HOVER}; 
                    border-color: {CyberpunkColors.BORDER_LIGHT};
                }}
                QPushButton:pressed {{ 
                    background-color: {CyberpunkColors.BG_ACTIVE}; 
                }}
                QPushButton:focus {{ 
                    border: 2px solid {CyberpunkColors.NEON_CYAN}; 
                    background-color: {CyberpunkColors.BG_ELEVATED};
                }}
                QPushButton:disabled {{
                    background-color: {CyberpunkColors.BG_SURFACE};
                    color: {CyberpunkColors.TEXT_DISABLED};
                    border-color: {CyberpunkColors.BORDER_DEFAULT};
                }}
            """,
            
            'primary': f"""
                QPushButton {{ 
                    background-color: {CyberpunkColors.NEON_CYAN}; 
                    color: {CyberpunkColors.BG_VOID}; 
                    border: 2px solid {CyberpunkColors.NEON_CYAN}; 
                    padding: 10px 20px; 
                    border-radius: {CyberpunkSizes.RADIUS_MD}px; 
                    font-weight: bold;
                    font-size: {CyberpunkTypography.SIZE_M}px;
                }}
                QPushButton:hover {{ 
                    background-color: {CyberpunkColors.NEON_CYAN_DIM}; 
                    border-color: {CyberpunkColors.NEON_CYAN_DIM};
                }}
                QPushButton:pressed {{ 
                    background-color: {CyberpunkColors.NEON_CYAN_DIM}; 
                }}
                QPushButton:focus {{ 
                    border: 3px solid {CyberpunkColors.TEXT_PRIMARY}; 
                }}
            """,
            
            'success': f"""
                QPushButton {{ 
                    background-color: {CyberpunkColors.NEON_GREEN}; 
                    color: {CyberpunkColors.BG_VOID}; 
                    border: 2px solid {CyberpunkColors.NEON_GREEN}; 
                    padding: 10px 20px; 
                    border-radius: {CyberpunkSizes.RADIUS_MD}px; 
                    font-weight: bold;
                    font-size: {CyberpunkTypography.SIZE_M}px;
                }}
                QPushButton:hover {{ 
                    background-color: {CyberpunkColors.NEON_GREEN_DIM}; 
                    border-color: {CyberpunkColors.NEON_GREEN_DIM};
                }}
                QPushButton:pressed {{ 
                    background-color: {CyberpunkColors.NEON_GREEN_DIM}; 
                }}
                QPushButton:focus {{ 
                    border: 3px solid {CyberpunkColors.TEXT_PRIMARY}; 
                }}
            """,
            
            'warning': f"""
                QPushButton {{ 
                    background-color: {CyberpunkColors.NEON_ORANGE}; 
                    color: {CyberpunkColors.BG_VOID}; 
                    border: 2px solid {CyberpunkColors.NEON_ORANGE}; 
                    padding: 10px 20px; 
                    border-radius: {CyberpunkSizes.RADIUS_MD}px; 
                    font-weight: bold;
                    font-size: {CyberpunkTypography.SIZE_M}px;
                }}
                QPushButton:hover {{ 
                    background-color: {CyberpunkColors.NEON_ORANGE_DIM}; 
                    border-color: {CyberpunkColors.NEON_ORANGE_DIM};
                }}
                QPushButton:pressed {{ 
                    background-color: {CyberpunkColors.NEON_ORANGE_DIM}; 
                }}
                QPushButton:focus {{ 
                    border: 3px solid {CyberpunkColors.TEXT_PRIMARY}; 
                }}
            """,
            
            'danger': f"""
                QPushButton {{ 
                    background-color: {CyberpunkColors.NEON_PINK}; 
                    color: {CyberpunkColors.TEXT_PRIMARY}; 
                    border: 2px solid {CyberpunkColors.NEON_PINK}; 
                    padding: 10px 20px; 
                    border-radius: {CyberpunkSizes.RADIUS_MD}px; 
                    font-weight: bold;
                    font-size: {CyberpunkTypography.SIZE_M}px;
                }}
                QPushButton:hover {{ 
                    background-color: {CyberpunkColors.NEON_PINK_DIM}; 
                    border-color: {CyberpunkColors.NEON_PINK_DIM};
                }}
                QPushButton:pressed {{ 
                    background-color: {CyberpunkColors.NEON_PINK_DIM}; 
                }}
                QPushButton:focus {{ 
                    border: 3px solid {CyberpunkColors.TEXT_PRIMARY}; 
                }}
            """,
            
            'info': f"""
                QPushButton {{ 
                    background-color: {CyberpunkColors.NEON_PURPLE}; 
                    color: {CyberpunkColors.TEXT_PRIMARY}; 
                    border: 2px solid {CyberpunkColors.NEON_PURPLE}; 
                    padding: 10px 20px; 
                    border-radius: {CyberpunkSizes.RADIUS_MD}px; 
                    font-weight: bold;
                    font-size: {CyberpunkTypography.SIZE_M}px;
                }}
                QPushButton:hover {{ 
                    background-color: {CyberpunkColors.NEON_PURPLE_DIM}; 
                    border-color: {CyberpunkColors.NEON_PURPLE_DIM};
                }}
                QPushButton:pressed {{ 
                    background-color: {CyberpunkColors.NEON_PURPLE_DIM}; 
                }}
                QPushButton:focus {{ 
                    border: 3px solid {CyberpunkColors.TEXT_PRIMARY}; 
                }}
            """,
        }
        
        return styles.get(variant, styles['default'])
    
    # ========== CARD STYLE (CYBERPUNK) ==========
    
    @staticmethod
    def get_card_style(variant: str = 'default') -> str:
        """
        Get card/panel style - CYBERPUNK EDITION
        
        Variants:
        - default: Standard dark card
        - elevated: Elevated surface with border
        - neon: Card with neon border
        """
        styles = {
            'default': f"""
                QFrame {{
                    background-color: {CyberpunkColors.BG_SURFACE};
                    border: 1px solid {CyberpunkColors.BORDER_DEFAULT};
                    border-radius: {CyberpunkSizes.RADIUS_LG}px;
                    padding: {CyberpunkSpacing.LG}px;
                }}
            """,
            
            'elevated': f"""
                QFrame {{
                    background-color: {CyberpunkColors.BG_ELEVATED};
                    border: 2px solid {CyberpunkColors.BORDER_LIGHT};
                    border-radius: {CyberpunkSizes.RADIUS_LG}px;
                    padding: {CyberpunkSpacing.LG}px;
                }}
            """,
            
            'neon': f"""
                QFrame {{
                    background-color: {CyberpunkColors.BG_SURFACE};
                    border: 2px solid {CyberpunkColors.NEON_CYAN};
                    border-radius: {CyberpunkSizes.RADIUS_LG}px;
                    padding: {CyberpunkSpacing.LG}px;
                }}
            """,
        }
        
        return styles.get(variant, styles['default'])
    
    # ========== BUTTON SIZING ==========
    
    @staticmethod
    def apply_button_size(button, size='medium', width='auto'):
        """
        Apply standard size to button
        
        Args:
            button: QPushButton instance
            size: 'small' | 'medium' | 'large' | 'xlarge'
            width: 'auto' | 'narrow' | 'normal' | 'wide' | 'full' | int
        """
        heights = {
            'small': ButtonSize.SMALL,
            'medium': ButtonSize.MEDIUM,
            'large': ButtonSize.LARGE,
            'xlarge': ButtonSize.XLARGE,
        }
        height = heights.get(size, ButtonSize.MEDIUM)
        
        if width == 'auto':
            button.adjustSize()
            current_width = button.width()
            button.setMinimumWidth(max(current_width + 20, ButtonSize.MIN_WIDTH_NARROW))
        elif width == 'narrow':
            button.setFixedWidth(ButtonSize.MIN_WIDTH_NARROW)
        elif width == 'normal':
            button.setFixedWidth(ButtonSize.MIN_WIDTH_NORMAL)
        elif width == 'wide':
            button.setFixedWidth(ButtonSize.MIN_WIDTH_WIDE)
        elif width == 'full':
            button.setFixedWidth(ButtonSize.MIN_WIDTH_FULL)
        elif isinstance(width, int):
            button.setFixedWidth(width)
        
        button.setFixedHeight(height)
    
    @staticmethod
    def get_button_style_fixed(variant='default', width=100, height=40):
        """
        Get button style dengan FIXED SIZE (konsisten!)
        
        Args:
            variant: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info'
            width: Fixed width in pixels
            height: Fixed height in pixels
        
        Returns:
            str: Complete stylesheet dengan fixed size
        
        Usage:
            btn.setStyleSheet(StyleManager.get_button_style_fixed('primary', 120, 40))
        """
        base_style = StyleManager.get_button_style(variant)
        
        size_style = f"""
            QPushButton {{
                min-width: {width}px;
                max-width: {width}px;
                min-height: {height}px;
                max-height: {height}px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }}
        """
        
        return base_style + size_style
    
    @staticmethod
    def get_button_style_with_size(variant='default', size='medium'):
        """
        Get button style dengan size included
        
        Usage:
            btn.setStyleSheet(StyleManager.get_button_style_with_size('success', 'large'))
        """
        base_style = StyleManager.get_button_style(variant)
        
        paddings = {
            'small': '6px 12px',
            'medium': '10px 20px',
            'large': '12px 24px',
            'xlarge': '15px 30px',
        }
        padding = paddings.get(size, '10px 20px')
        
        heights = {
            'small': ButtonSize.SMALL,
            'medium': ButtonSize.MEDIUM,
            'large': ButtonSize.LARGE,
            'xlarge': ButtonSize.XLARGE,
        }
        min_height = heights.get(size, ButtonSize.MEDIUM)
        
        size_style = f"""
            QPushButton {{
                padding: {padding};
                min-height: {min_height}px;
            }}
        """
        
        return base_style + size_style