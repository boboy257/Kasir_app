"""
Help Overlay Widget
===================
F1 keyboard shortcuts help overlay - reusable for all windows
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve


class HelpOverlay(QWidget):
    """
    Transparent overlay dengan keyboard shortcuts help
    
    Usage:
        help = HelpOverlay(parent_window)
        help.set_shortcuts({"Category": [("Key", "Description")]})
        help.toggle()  # Show/hide
    """
    
    # Default global shortcuts
    DEFAULT_SHORTCUTS = {
        "Global": [
            ("ESC", "Tutup window / Kembali"),
            ("Ctrl+S", "Simpan data"),
            ("Ctrl+N", "Reset form / Baru"),
            ("Ctrl+F", "Focus ke pencarian"),
            ("F1", "Tampilkan help ini"),
        ]
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.shortcuts = {}
        self.setup_ui()
        self.is_animating = False
        self.hide()  # Initially hidden
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def setup_ui(self):
        """Setup overlay UI with dark theme"""
        # Full window overlay
        self.setGeometry(0, 0, 
                        self.parent().width() if self.parent() else 800,
                        self.parent().height() if self.parent() else 600)
        
        # Semi-transparent background
        self.setStyleSheet("""
            QWidget#HelpOverlay {
                background-color: rgba(0, 0, 0, 180);
            }
        """)
        self.setObjectName("HelpOverlay")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Content frame
        self.content_frame = QFrame()
        self.content_frame.setMaximumWidth(700)
        self.content_frame.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border: 2px solid #2196F3;
                border-radius: 15px;
            }
            QLabel {
                background: transparent;
                border: none;
            }
        """)
        
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        # Header
        lbl_title = QLabel("⌨️ KEYBOARD SHORTCUTS")
        lbl_title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2196F3;
            padding: 10px;
        """)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(lbl_title)
        
        # Scrollable shortcuts area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background-color: #2D2D2D;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 6px;
            }
        """)
        
        self.shortcuts_widget = QWidget()
        self.shortcuts_layout = QVBoxLayout(self.shortcuts_widget)
        self.shortcuts_layout.setSpacing(15)
        
        scroll.setWidget(self.shortcuts_widget)
        content_layout.addWidget(scroll)
        
        # Footer
        lbl_footer = QLabel("💡 Tekan F1 atau ESC untuk menutup help")
        lbl_footer.setStyleSheet("""
            font-size: 12px;
            color: #aaa;
            font-style: italic;
            padding: 10px;
        """)
        lbl_footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(lbl_footer)
        
        layout.addWidget(self.content_frame)
        
        # Fade animation
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    def set_shortcuts(self, shortcuts_dict: dict):
        """
        Set shortcuts to display
        
        Args:
            shortcuts_dict: {"Category": [("Key", "Description"), ...]}
        """
        self.shortcuts = shortcuts_dict
        self.render_shortcuts()
    
    def render_shortcuts(self):
        """Render shortcuts to UI"""
        # Clear existing widgets
        while self.shortcuts_layout.count():
            item = self.shortcuts_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Combine default + custom shortcuts
        all_shortcuts = {**self.DEFAULT_SHORTCUTS, **self.shortcuts}
        
        # Render each category
        for category, shortcuts_list in all_shortcuts.items():
            # Category header
            lbl_category = QLabel(f"📌 {category}")
            lbl_category.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #00E5FF;
                margin-top: 10px;
                padding: 5px 0;
                border-bottom: 1px solid #333;
            """)
            self.shortcuts_layout.addWidget(lbl_category)
            
            # Shortcuts rows
            for key, description in shortcuts_list:
                row = QWidget()
                row_layout = QVBoxLayout(row)
                row_layout.setContentsMargins(10, 5, 10, 5)
                row_layout.setSpacing(5)
                
                # Key + Description
                text = f"<span style='color: #4CAF50; font-weight: bold; font-size: 14px;'>{key}</span>" \
                       f"<span style='color: #888; margin: 0 10px;'>→</span>" \
                       f"<span style='color: #E0E0E0; font-size: 13px;'>{description}</span>"
                
                lbl = QLabel(text)
                lbl.setTextFormat(Qt.TextFormat.RichText)
                lbl.setWordWrap(True)
                row_layout.addWidget(lbl)
                
                # Separator line
                sep = QFrame()
                sep.setFrameShape(QFrame.Shape.HLine)
                sep.setStyleSheet("background-color: #2D2D2D; max-height: 1px;")
                row_layout.addWidget(sep)
                
                self.shortcuts_layout.addWidget(row)
        
        self.shortcuts_layout.addStretch()
    
    def show_animated(self):
        """Show with fade-in animation"""
        if self.is_animating:
            return
        
        self.is_animating = True
        self.show()
        self.raise_()
        self.setFocus()
        
        # Disconnect semua signal dulu
        try:
            self.fade_animation.finished.disconnect()
        except:
            pass
        
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.finished.connect(self._on_show_finished)  
        self.fade_animation.start()

    def hide_animated(self):
        """Hide with fade-out animation"""
        if self.is_animating:
            return
        
        self.is_animating = True
        
        # Disconnect semua signal dulu
        try:
            self.fade_animation.finished.disconnect()
        except:
            pass
        
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self._on_hide_finished)  
        self.fade_animation.start()

    def _on_show_finished(self):
        """Called when show animation finished"""
        self.is_animating = False

    def _on_hide_finished(self):
        """Called when hide animation finished"""
        self.hide()
        self.is_animating = False
    
    def toggle(self):
        """Toggle visibility"""
        if self.is_animating:
            return
        if self.isVisible():
            self.hide_animated()
        else:
            self.show_animated()
    
    def keyPressEvent(self, event):
        """Handle ESC and F1 to close"""
        if event.key() == Qt.Key.Key_Escape:
            self.hide_animated()
        else:
            super().keyPressEvent(event)
    
    def resizeEvent(self, event):
        """Resize with parent window"""
        if self.parent():
            self.setGeometry(0, 0, self.parent().width(), self.parent().height())
        super().resizeEvent(event)