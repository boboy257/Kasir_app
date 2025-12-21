"""
Style Manager
=============
Centralized style management untuk konsistensi UI
"""

from pathlib import Path
from PyQt6.QtWidgets import QApplication

# ========== BUTTON SIZE CONSTANTS ==========

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
    Singleton class untuk manage styles
    
    Features:
    - Load theme dari QSS file
    - Get colors by name
    - Get component styles by variant
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
        """
        Load theme dari QSS file
        
        Args:
            theme: Theme name (dark/light)
            
        Returns:
            True jika berhasil
        """
        qss_file = self.styles_path / f"{theme}_theme.qss"
        
        if qss_file.exists():
            try:
                with open(qss_file, 'r', encoding='utf-8') as f:
                    stylesheet = f.read()
                
                # Apply ke entire application
                QApplication.instance().setStyleSheet(stylesheet)
                self.current_theme = theme
                return True
            except Exception as e:
                print(f"Error loading theme: {e}")
                return False
        else:
            print(f"Theme file not found: {qss_file}")
            return False
    
    # ========== COLOR PALETTE ==========
    
    @staticmethod
    def get_color(name: str) -> str:
        """
        Get color by name - UPDATED PALETTE
        
        Design principles:
        - Primary: Blue (professional, trust)
        - Success: Green (positive action)
        - Warning: Orange (caution)
        - Danger: Red (destructive action)
        - Neutral: Grays (backgrounds, borders)
        """
        colors = {
            # ========== PRIMARY COLORS ==========
            'primary': '#2196F3',        # Blue - Main brand color
            'primary-light': '#64B5F6',  # Light blue - Hover
            'primary-dark': '#1976D2',   # Dark blue - Active
            
            # ========== SEMANTIC COLORS ==========
            'success': '#4CAF50',        # Green - Success, positive
            'success-light': '#66BB6A',  # Light green - Hover
            'success-dark': '#388E3C',   # Dark green - Active
            
            'warning': '#FF9800',        # Orange - Warning, attention
            'warning-light': '#FFB74D',  # Light orange - Hover
            'warning-dark': '#F57C00',   # Dark orange - Active
            
            'danger': '#F44336',         # Red - Error, delete
            'danger-light': '#EF5350',   # Light red - Hover
            'danger-dark': '#D32F2F',    # Dark red - Active
            
            'info': '#00BCD4',           # Cyan - Info, neutral action
            'info-light': '#4DD0E1',     # Light cyan - Hover
            'info-dark': '#0097A7',      # Dark cyan - Active
            
            # ========== BACKGROUND COLORS ==========
            'bg-app': '#0D0D0D',         # App background (darkest)
            'bg-window': '#121212',      # Window background
            'bg-surface': '#1E1E1E',     # Surface (cards, panels)
            'bg-elevated': '#252525',    # Elevated surface (dialogs)
            'bg-input': '#1E1E1E',       # Input fields
            'bg-hover': '#2D2D2D',       # Hover state
            'bg-active': '#333333',      # Active/pressed state
            
            # ========== TEXT COLORS ==========
            'text-primary': '#FFFFFF',   # Primary text (white)
            'text-secondary': '#B0B0B0', # Secondary text (gray)
            'text-disabled': '#666666',  # Disabled text
            'text-placeholder': '#808080', # Placeholder text
            
            # ========== BORDER COLORS ==========
            'border': '#333333',         # Default border
            'border-light': '#404040',   # Light border
            'border-focus': '#2196F3',   # Focus border (blue)
            'border-error': '#F44336',   # Error border (red)
            
            # ========== ACCENT COLORS ==========
            'accent-purple': '#9C27B0',  # Purple - Pending
            'accent-cyan': '#00E5FF',    # Bright cyan - Highlight
            'accent-teal': '#009688',    # Teal - Special actions
            'accent-amber': '#FFC107',   # Amber - Alerts
        }
        return colors.get(name, '#FFFFFF')
    
    # ========== BUTTON STYLES ==========
    
    @staticmethod
    def get_button_style(variant: str = 'default') -> str:
        """
        Get button style - UPDATED dengan color palette
        
        Variants:
        - default: Neutral gray button
        - primary: Blue - Main actions
        - success: Green - Positive actions (save, confirm)
        - warning: Orange - Caution actions (edit, pending)
        - danger: Red - Destructive actions (delete)
        - info: Cyan - Info actions
        """
        
        # Get colors
        from src.ui.base.style_manager import StyleManager
        c = StyleManager.get_color
        
        styles = {
            'default': f"""
                QPushButton {{ 
                    background-color: {c('bg-surface')}; 
                    color: {c('text-primary')}; 
                    border: 2px solid {c('border')}; 
                    padding: 10px 20px; 
                    border-radius: 5px; 
                    font-weight: bold;
                    font-size: 13px;
                }}
                QPushButton:hover {{ 
                    background-color: {c('bg-hover')}; 
                    border-color: {c('border-light')};
                }}
                QPushButton:pressed {{ 
                    background-color: {c('bg-active')}; 
                }}
                QPushButton:focus {{ 
                    border: 2px solid {c('border-focus')}; 
                    background-color: {c('bg-elevated')}; 
                }}
                QPushButton:disabled {{
                    background-color: {c('bg-surface')};
                    color: {c('text-disabled')};
                    border-color: {c('border')};
                }}
            """,
            
            'primary': f"""
                QPushButton {{ 
                    background-color: {c('primary')}; 
                    color: {c('text-primary')}; 
                    border: 2px solid {c('primary')}; 
                    padding: 10px 20px; 
                    border-radius: 5px; 
                    font-weight: bold;
                    font-size: 13px;
                }}
                QPushButton:hover {{ 
                    background-color: {c('primary-light')}; 
                    border-color: {c('primary-light')};
                }}
                QPushButton:pressed {{ 
                    background-color: {c('primary-dark')}; 
                }}
                QPushButton:focus {{ 
                    border: 2px solid {c('text-primary')}; 
                }}
            """,
            
            'success': f"""
                QPushButton {{ 
                    background-color: {c('success')}; 
                    color: {c('text-primary')}; 
                    border: 2px solid {c('success')}; 
                    padding: 10px 20px; 
                    border-radius: 5px; 
                    font-weight: bold;
                    font-size: 13px;
                }}
                QPushButton:hover {{ 
                    background-color: {c('success-light')}; 
                }}
                QPushButton:pressed {{ 
                    background-color: {c('success-dark')}; 
                }}
                QPushButton:focus {{ 
                    border: 2px solid {c('text-primary')}; 
                }}
            """,
            
            'warning': f"""
                QPushButton {{ 
                    background-color: {c('warning')}; 
                    color: {c('text-primary')}; 
                    border: 2px solid {c('warning')}; 
                    padding: 10px 20px; 
                    border-radius: 5px; 
                    font-weight: bold;
                    font-size: 13px;
                }}
                QPushButton:hover {{ 
                    background-color: {c('warning-light')}; 
                }}
                QPushButton:pressed {{ 
                    background-color: {c('warning-dark')}; 
                }}
                QPushButton:focus {{ 
                    border: 2px solid {c('text-primary')}; 
                }}
            """,
            
            'danger': f"""
                QPushButton {{ 
                    background-color: {c('danger')}; 
                    color: {c('text-primary')}; 
                    border: 2px solid {c('danger')}; 
                    padding: 10px 20px; 
                    border-radius: 5px; 
                    font-weight: bold;
                    font-size: 13px;
                }}
                QPushButton:hover {{ 
                    background-color: {c('danger-light')}; 
                }}
                QPushButton:pressed {{ 
                    background-color: {c('danger-dark')}; 
                }}
                QPushButton:focus {{ 
                    border: 2px solid {c('text-primary')}; 
                }}
            """,
            
            'info': f"""
                QPushButton {{ 
                    background-color: {c('info')}; 
                    color: {c('text-primary')}; 
                    border: 2px solid {c('info')}; 
                    padding: 10px 20px; 
                    border-radius: 5px; 
                    font-weight: bold;
                    font-size: 13px;
                }}
                QPushButton:hover {{ 
                    background-color: {c('info-light')}; 
                }}
                QPushButton:pressed {{ 
                    background-color: {c('info-dark')}; 
                }}
                QPushButton:focus {{ 
                    border: 2px solid {c('text-primary')}; 
                }}
            """,
        }
        
        return styles.get(variant, styles['default'])
    
    



    # ========== ADD TO StyleManager CLASS ==========

    @staticmethod
    def apply_button_size(button, size='medium', width='auto'):
        """
        Apply standard size to button
        
        Args:
            button: QPushButton instance
            size: 'small' | 'medium' | 'large' | 'xlarge'
            width: 'auto' | 'narrow' | 'normal' | 'wide' | 'full' | int
        
        Usage:
            StyleManager.apply_button_size(btn, 'large', 'wide')
        """
        from src.ui.base.style_manager import ButtonSize
        
        # Set height
        heights = {
            'small': ButtonSize.SMALL,
            'medium': ButtonSize.MEDIUM,
            'large': ButtonSize.LARGE,
            'xlarge': ButtonSize.XLARGE,
        }
        height = heights.get(size, ButtonSize.MEDIUM)
        
        # Set width
        if width == 'auto':
            # Auto width based on text
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
    def get_button_style_with_size(variant='default', size='medium'):
        """
        Get button style dengan size included
        
        Usage:
            btn.setStyleSheet(StyleManager.get_button_style_with_size('success', 'large'))
        """
        from src.ui.base.style_manager import StyleManager, ButtonSize
        
        base_style = StyleManager.get_button_style(variant)
        
        # Add size-specific padding
        paddings = {
            'small': '6px 12px',
            'medium': '10px 20px',
            'large': '12px 24px',
            'xlarge': '15px 30px',
        }
        padding = paddings.get(size, '10px 20px')
        
        # Add min-height
        heights = {
            'small': ButtonSize.SMALL,
            'medium': ButtonSize.MEDIUM,
            'large': ButtonSize.LARGE,
            'xlarge': ButtonSize.XLARGE,
        }
        min_height = heights.get(size, ButtonSize.MEDIUM)
        
        # Inject padding & min-height into style
        size_style = f"""
            QPushButton {{
                padding: {padding};
                min-height: {min_height}px;
            }}
        """
        
        return base_style + size_style