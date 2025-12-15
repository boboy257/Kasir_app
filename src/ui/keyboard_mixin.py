"""
Keyboard Navigation Mixin
Standardisasi navigasi keyboard untuk semua window.
"""

from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtWidgets import QTableWidget

class KeyboardNavigationMixin:
    """
    Mixin class untuk navigasi keyboard standar.
    
    Usage:
        class MyWindow(QMainWindow, KeyboardNavigationMixin):
            def __init__(self):
                super().__init__()
                # ... setup UI ...
                self.setup_keyboard_navigation()
    """
    
    def setup_keyboard_navigation(self):
        """
        Setup navigasi keyboard otomatis.
        Override method ini di subclass untuk custom behavior.
        """
        self.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Global event filter dengan behavior standar"""
        
        # Hanya proses KeyPress event
        if event.type() != QEvent.Type.KeyPress:
            return super().eventFilter(obj, event)
        
        key = event.key()
        
        # ESC = Tutup window (global untuk semua window)
        if key == Qt.Key.Key_Escape:
            self.handle_escape()
            return True
        
        # Delegasi ke handler spesifik
        if self.handle_navigation(obj, key):
            return True
        
        return super().eventFilter(obj, event)
    
    def handle_escape(self):
        """
        Handle ESC key.
        Override di subclass untuk custom behavior.
        """
        self.close()
    
    def handle_navigation(self, obj, key):
        """
        Handle arrow keys dan Enter.
        Override di subclass untuk custom navigation logic.
        
        Returns:
            bool: True jika event sudah dihandle
        """
        # Default behavior untuk tabel
        if isinstance(obj, QTableWidget):
            return self.handle_table_navigation(obj, key)
        
        return False
    
    def handle_table_navigation(self, table, key):
        """
        Navigasi standar untuk QTableWidget.
        
        - Arrow Up di baris 0 → Fokus ke widget sebelumnya
        - Arrow Down di baris terakhir → Fokus ke widget berikutnya
        - Enter → Trigger action (override handle_table_enter)
        """
        current_row = table.currentRow()
        total_rows = table.rowCount()
        
        # Arrow Up di baris pertama
        if key == Qt.Key.Key_Up and current_row == 0:
            prev_widget = self.get_widget_before_table(table)
            if prev_widget:
                prev_widget.setFocus()
                return True
        
        # Arrow Down di baris terakhir
        elif key == Qt.Key.Key_Down and current_row == total_rows - 1:
            next_widget = self.get_widget_after_table(table)
            if next_widget:
                next_widget.setFocus()
                return True
        
        # Enter di tabel
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.handle_table_enter(table)
            return True
        
        return False
    
    def get_widget_before_table(self, table):
        """
        Override di subclass untuk return widget sebelum tabel.
        
        Example:
            return self.input_cari
        """
        return None
    
    def get_widget_after_table(self, table):
        """
        Override di subclass untuk return widget setelah tabel.
        
        Example:
            return self.btn_first
        """
        return None
    
    def handle_table_enter(self, table):
        """
        Override di subclass untuk handle Enter di tabel.
        
        Example:
            self.lihat_detail()
        """
        pass
    
    def setup_button_navigation(self, buttons):
        """
        Helper untuk setup navigasi horizontal buttons.
        
        Args:
            buttons: List of buttons [btn1, btn2, btn3]
        
        Example:
            self.setup_button_navigation([
                self.btn_detail,
                self.btn_print,
                self.btn_export
            ])
        """
        self._button_list = buttons
        
        for i, btn in enumerate(buttons):
            btn.installEventFilter(self)
            btn.setProperty('nav_index', i)
    
    def handle_button_navigation(self, button, key):
        """Navigasi horizontal antar buttons"""
        if not hasattr(self, '_button_list'):
            return False
        
        nav_index = button.property('nav_index')
        if nav_index is None:
            return False
        
        # Arrow Right
        if key == Qt.Key.Key_Right:
            if nav_index + 1 < len(self._button_list):
                self._button_list[nav_index + 1].setFocus()
                return True
        
        # Arrow Left
        elif key == Qt.Key.Key_Left:
            if nav_index - 1 >= 0:
                self._button_list[nav_index - 1].setFocus()
                return True
        
        # Arrow Up (balik ke tabel/input)
        elif key == Qt.Key.Key_Up:
            prev_widget = self.get_widget_before_buttons()
            if prev_widget:
                prev_widget.setFocus()
                if isinstance(prev_widget, QTableWidget) and prev_widget.rowCount() > 0:
                    prev_widget.selectRow(prev_widget.rowCount() - 1)
                return True
        
        # Enter
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            button.click()
            return True
        
        return False
    
    def get_widget_before_buttons(self):
        """
        Override di subclass untuk return widget sebelum buttons.
        
        Example:
            return self.table
        """
        return None