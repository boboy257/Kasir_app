"""
Style Manager
=============
Centralized style management untuk konsistensi UI
"""

from pathlib import Path
from PyQt6.QtWidgets import QApplication

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
        Get color by name
        
        Args:
            name: Color name (primary, success, warning, danger, etc)
            
        Returns:
            Hex color code
        """
        colors = {
            # Brand colors
            'primary': '#2196F3',
            'secondary': '#00E5FF',
            
            # Status colors
            'success': '#4CAF50',
            'warning': '#FF9800',
            'danger': '#F44336',
            'info': '#00BCD4',
            
            # Background colors
            'background': '#121212',
            'surface': '#1E1E1E',
            'elevated': '#252525',
            
            # Text colors
            'text': '#e0e0e0',
            'text-secondary': '#aaaaaa',
            'text-disabled': '#666666',
            
            # Border colors
            'border': '#333333',
            'border-focus': '#2196F3',
        }
        return colors.get(name, '#FFFFFF')
    
    # ========== BUTTON STYLES ==========
    
    @staticmethod
    def get_button_style(variant: str = 'default') -> str:
        """
        Get button style by variant
        
        Args:
            variant: Button variant (default, primary, success, warning, danger)
            
        Returns:
            CSS stylesheet string
        """
        styles = {
            'default': """
                QPushButton { 
                    background-color: #1E1E1E; 
                    border: 2px solid #333; 
                    padding: 10px 20px; 
                    border-radius: 4px; 
                    font-weight: bold;
                    color: #e0e0e0;
                }
                QPushButton:hover { background-color: #333; }
                QPushButton:focus { 
                    border: 2px solid #ffffff; 
                    background-color: #424242; 
                }
            """,
            
            'primary': """
                QPushButton { 
                    background-color: #2196F3; 
                    color: white; 
                    border: 2px solid #2196F3; 
                    padding: 10px 20px; 
                    border-radius: 4px; 
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #1976D2; }
                QPushButton:focus { 
                    border: 2px solid #ffffff; 
                    background-color: #1976D2; 
                }
            """,
            
            'success': """
                QPushButton { 
                    background-color: #4CAF50; 
                    color: white; 
                    border: 2px solid #4CAF50; 
                    padding: 10px 20px; 
                    border-radius: 4px; 
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #45a049; }
                QPushButton:focus { 
                    border: 2px solid #ffffff; 
                    background-color: #43A047; 
                }
            """,
            
            'warning': """
                QPushButton { 
                    background-color: #FF9800; 
                    color: white; 
                    border: 2px solid #FF9800; 
                    padding: 10px 20px; 
                    border-radius: 4px; 
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #F57C00; }
                QPushButton:focus { 
                    border: 2px solid #ffffff; 
                    background-color: #F57C00; 
                }
            """,
            
            'danger': """
                QPushButton { 
                    background-color: #F44336; 
                    color: white; 
                    border: 2px solid #F44336; 
                    padding: 10px 20px; 
                    border-radius: 4px; 
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #d32f2f; }
                QPushButton:focus { 
                    border: 2px solid #ffffff; 
                    background-color: #c62828; 
                }
            """,
        }
        return styles.get(variant, styles['default'])