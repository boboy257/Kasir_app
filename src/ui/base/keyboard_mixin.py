"""Keyboard Navigation Mixin - Centralized keyboard handling"""

from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtWidgets import QTableWidget, QLineEdit, QTextEdit


class KeyboardMixin:
    """Mixin for consistent keyboard navigation across all windows"""
    
    def setup_keyboard_navigation(self):
        """Initialize keyboard navigation system"""
        self._navigation_map = {}
        self._shortcut_map = {}
        self._table_callbacks = {}
        self.installEventFilter(self)
    
    def register_navigation(self, widget, navigation_dict: dict):
        """Register basic arrow/enter navigation"""
        widget.installEventFilter(self)
        self._navigation_map[widget] = navigation_dict
    
    def register_shortcut(self, key: Qt.Key, callback, modifiers=None):
        """Register global shortcut"""
        shortcut_key = (key, modifiers) if modifiers else key
        self._shortcut_map[shortcut_key] = callback
    
    def register_table_callbacks(self, table, callbacks: dict):
        """Register callbacks for table actions (edit, delete, focus_up, focus_down)"""
        table.installEventFilter(self)
        self._table_callbacks[table] = callbacks
    
    def eventFilter(self, obj, event):
        """Main event filter - handles all keyboard events"""
        if event.type() == QEvent.Type.KeyPress:
            if self._handle_global_shortcuts(event):
                return True
            
            if isinstance(obj, QTableWidget):
                if self._handle_table_shortcuts(obj, event):
                    return True
            
            if obj in self._navigation_map:
                if self._handle_widget_navigation(obj, event):
                    return True
        
        # FIX: Return False instead of super().eventFilter()
        return False
    
    def _handle_global_shortcuts(self, event) -> bool:
        """Handle global shortcuts"""
        key = event.key()
        modifiers = event.modifiers()
        
        if key in self._shortcut_map:
            self._shortcut_map[key]()
            return True
        
        if (key, modifiers) in self._shortcut_map:
            self._shortcut_map[(key, modifiers)]()
            return True
        
        if key == Qt.Key.Key_Escape:
            return self.handle_escape()
        
        if modifiers == Qt.KeyboardModifier.ControlModifier:
            if key == Qt.Key.Key_S:
                if hasattr(self, 'simpan'):
                    self.simpan()
                    return True
                elif hasattr(self, 'save'):
                    self.save()
                    return True
            
            if key == Qt.Key.Key_N:
                if hasattr(self, 'reset_form'):
                    self.reset_form()
                    return True
            
            if key == Qt.Key.Key_F:
                if hasattr(self, 'input_cari'):
                    self.input_cari.setFocus()
                    self.input_cari.selectAll()
                    return True
        
        return False
    
    def _handle_table_shortcuts(self, table, event) -> bool:
        """Handle table-specific shortcuts"""
        key = event.key()
        modifiers = event.modifiers()
        row = table.currentRow()
        
        callbacks = self._table_callbacks.get(table, {})
        
        if key in (Qt.Key.Key_F2, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if 'edit' in callbacks:
                callbacks['edit']()
                return True
        
        if key == Qt.Key.Key_Delete:
            if 'delete' in callbacks:
                callbacks['delete']()
                return True
        
        if modifiers == Qt.KeyboardModifier.ControlModifier:
            if key == Qt.Key.Key_Up:
                if 'focus_up' in callbacks:
                    target = callbacks['focus_up']
                    if callable(target):
                        target()
                    else:
                        target.setFocus()
                        if hasattr(target, 'selectAll'):
                            target.selectAll()
                    return True
            
            if key == Qt.Key.Key_Down:
                if 'focus_down' in callbacks:
                    target = callbacks['focus_down']
                    if callable(target):
                        target()
                    else:
                        target.setFocus()
                    return True
        
        if key == Qt.Key.Key_Up and row == 0:
            if 'focus_up' in callbacks:
                target = callbacks['focus_up']
                if callable(target):
                    target()
                else:
                    target.setFocus()
                    if hasattr(target, 'selectAll'):
                        target.selectAll()
                return True
        
        if key == Qt.Key.Key_Down and row == table.rowCount() - 1:
            if 'focus_down' in callbacks:
                target = callbacks['focus_down']
                if callable(target):
                    target()
                else:
                    target.setFocus()
                return True
        
        return False
    
    def _handle_widget_navigation(self, widget, event) -> bool:
        """Handle widget-specific navigation"""
        nav_dict = self._navigation_map[widget]
        key = event.key()
        
        if key in nav_dict:
            target = nav_dict[key]
            
            if callable(target):
                target()
            elif target is not None:
                target.setFocus()
                if isinstance(target, (QLineEdit, QTextEdit)) and hasattr(target, 'selectAll'):
                    target.selectAll()
            
            return True
        
        return False
    
    def handle_escape(self) -> bool:
        """Handle ESC key - override in subclass"""
        self.close()
        return True
    
    def focus_table_first_row(self, table):
        """Helper: Focus table & select first row"""
        if table.rowCount() > 0:
            table.setFocus()
            table.selectRow(0)
    
    def focus_table_last_row(self, table):
        """Helper: Focus table & select last row"""
        if table.rowCount() > 0:
            table.setFocus()
            table.selectRow(table.rowCount() - 1)