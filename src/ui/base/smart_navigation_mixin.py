"""
Smart Navigation Mixin - ULTIMATE SYSTEM
=========================================
✅ Circular navigation (Right terus = balik ke awal)
✅ Navigation memory (ingat dari mana user datang)
✅ Focus stack (bisa undo navigation)
✅ Auto boundary check
✅ Grid navigation support
✅ Backward compatible dengan KeyboardMixin lama

Author: Claude + Your Input
Created: 2024
"""

from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtWidgets import QTableWidget, QLineEdit, QTextEdit


class SmartNavigationMixin:
    """
    Smart keyboard navigation dengan features:
    - Circular navigation
    - Navigation memory
    - Focus stack
    - Grid support
    """
    
    def setup_keyboard_navigation(self):
        """Initialize smart navigation system"""
        self._navigation_map = {}
        self._shortcut_map = {}
        self._table_callbacks = {}
        self._navigation_grids = []  # ✅ NEW: Grid navigation
        self._focus_history = []     # ✅ NEW: Navigation memory
        self._last_focused_widget = None
        self.installEventFilter(self)
    
    # ========== BASIC NAVIGATION (Compatible dengan system lama) ==========
    
    def register_navigation(self, widget, navigation_dict: dict):
        """
        Register basic navigation (BACKWARD COMPATIBLE)
        
        ✅ NEW: Support 'circular' option
        
        Example:
            self.register_navigation(self.btn_pdf, {
                Qt.Key.Key_Left: self.btn_csv,
                Qt.Key.Key_Right: self.btn_filter,  # Circular!
            })
        """
        widget.installEventFilter(self)
        self._navigation_map[widget] = navigation_dict
    
    def register_shortcut(self, key: Qt.Key, callback, modifiers=None):
        """Register global shortcut"""
        shortcut_key = (key, modifiers) if modifiers else key
        self._shortcut_map[shortcut_key] = callback
    
    def register_table_callbacks(self, table, callbacks: dict):
        """Register table callbacks"""
        table.installEventFilter(self)
        self._table_callbacks[table] = callbacks
    
    # ========== SMART NAVIGATION (NEW!) ==========
    
    def register_navigation_row(self, widgets: list, circular: bool = True):
        """
        Register horizontal navigation (row of widgets)
        
        ✅ Auto circular navigation
        ✅ Auto boundary check
        
        Args:
            widgets: List of widgets [btn1, btn2, btn3, ...]
            circular: If True, Right dari akhir = balik ke awal
        
        Example:
            self.register_navigation_row([
                self.btn_filter, self.btn_reset, 
                self.btn_csv, self.btn_pdf
            ], circular=True)
        """
        for i, widget in enumerate(widgets):
            widget.installEventFilter(self)
            
            nav_dict = {}
            
            # Left navigation
            if i > 0:
                nav_dict[Qt.Key.Key_Left] = widgets[i - 1]
            elif circular:
                # Circular: Left dari awal = ke akhir
                nav_dict[Qt.Key.Key_Left] = widgets[-1]
            
            # Right navigation
            if i < len(widgets) - 1:
                nav_dict[Qt.Key.Key_Right] = widgets[i + 1]
            elif circular:
                # Circular: Right dari akhir = ke awal
                nav_dict[Qt.Key.Key_Right] = widgets[0]
            
            self._navigation_map[widget] = nav_dict
    
    def register_navigation_grid(self, grid: list, circular: bool = False):
        """
        Register 2D grid navigation
        
        ✅ Auto Up/Down/Left/Right
        ✅ Support different row lengths
        ✅ Auto boundary handling
        
        Args:
            grid: List of rows, each row is list of widgets
                  [[row1_widget1, row1_widget2],
                   [row2_widget1]]
            circular: If True, edges wrap around
        
        Example:
            self.register_navigation_grid([
                [self.date_start, self.date_end, self.btn_filter],  # Row 1
                [self.table],                                        # Row 2
            ])
        """
        grid_data = {
            'grid': grid,
            'circular': circular
        }
        self._navigation_grids.append(grid_data)
        
        # Install event filters
        for row in grid:
            for widget in row:
                if widget:
                    widget.installEventFilter(self)
    
    def register_navigation_with_memory(self, from_widgets: list, to_widget, 
                                       key: Qt.Key = Qt.Key.Key_Down):
        """
        Register navigation dengan memory (ingat dari mana datang)
        
        ✅ Up/Down dengan memory
        
        Args:
            from_widgets: List of source widgets
            to_widget: Target widget (biasanya table)
            key: Trigger key (default Down)
        
        Example:
            # Dari button row ke table
            self.register_navigation_with_memory(
                from_widgets=[self.btn_filter, self.btn_reset, 
                             self.btn_csv, self.btn_pdf],
                to_widget=self.table,
                key=Qt.Key.Key_Down
            )
        """
        for widget in from_widgets:
            if widget not in self._navigation_map:
                self._navigation_map[widget] = {}
            
            # Store special marker untuk memory navigation
            self._navigation_map[widget][key] = {
                '_memory_nav': True,
                'target': to_widget,
                'source_group': from_widgets
            }
    
    # ========== EVENT FILTER ==========
    
    def eventFilter(self, obj, event):
        """Main event filter with smart features"""
        if event.type() == QEvent.Type.KeyPress:
            # Track focus history
            if obj != self._last_focused_widget:
                self._focus_history.append(self._last_focused_widget)
                if len(self._focus_history) > 10:  # Keep last 10
                    self._focus_history.pop(0)
                self._last_focused_widget = obj
            
            # Handle global shortcuts first
            if self._handle_global_shortcuts(event):
                return True
            
            # Handle grid navigation
            if self._handle_grid_navigation(obj, event):
                return True
            
            # Handle table shortcuts
            if isinstance(obj, QTableWidget):
                if self._handle_table_shortcuts(obj, event):
                    return True
            
            # Handle widget navigation (dengan memory support)
            if obj in self._navigation_map:
                if self._handle_widget_navigation(obj, event):
                    return True
        
        return False
    
    def _handle_global_shortcuts(self, event) -> bool:
        """Handle global shortcuts"""
        key = event.key()
        modifiers = event.modifiers()
        
        # Check registered shortcuts
        if key in self._shortcut_map:
            self._shortcut_map[key]()
            return True
        
        if (key, modifiers) in self._shortcut_map:
            self._shortcut_map[(key, modifiers)]()
            return True
        
        # ESC key
        if key == Qt.Key.Key_Escape:
            return self.handle_escape()
        
        # Ctrl shortcuts
        if modifiers == Qt.KeyboardModifier.ControlModifier:
            # Ctrl+S = Save (dengan multiple fallbacks)
            if key == Qt.Key.Key_S:
                for method_name in ['simpan', 'save', 'simpan_data', 
                                   'simpan_produk', 'simpan_user']:
                    if hasattr(self, method_name):
                        getattr(self, method_name)()
                        return True
            
            # Ctrl+N = Reset
            if key == Qt.Key.Key_N:
                if hasattr(self, 'reset_form'):
                    self.reset_form()
                    return True
            
            # Ctrl+F = Focus search
            if key == Qt.Key.Key_F:
                if hasattr(self, 'input_cari'):
                    self.input_cari.setFocus()
                    self.input_cari.selectAll()
                    return True
        
        return False
    
    def _handle_grid_navigation(self, obj, event) -> bool:
        """Handle grid navigation (2D)"""
        key = event.key()
        
        for grid_data in self._navigation_grids:
            grid = grid_data['grid']
            circular = grid_data['circular']
            
            # Find current position in grid
            current_pos = None
            for row_idx, row in enumerate(grid):
                for col_idx, widget in enumerate(row):
                    if widget == obj:
                        current_pos = (row_idx, col_idx)
                        break
                if current_pos:
                    break
            
            if not current_pos:
                continue
            
            row_idx, col_idx = current_pos
            target = None
            
            # Navigation logic
            if key == Qt.Key.Key_Up:
                if row_idx > 0:
                    target_row = grid[row_idx - 1]
                    # Smart column selection (stay in same column if possible)
                    target = target_row[min(col_idx, len(target_row) - 1)]
                elif circular:
                    target_row = grid[-1]
                    target = target_row[min(col_idx, len(target_row) - 1)]
            
            elif key == Qt.Key.Key_Down:
                if row_idx < len(grid) - 1:
                    target_row = grid[row_idx + 1]
                    target = target_row[min(col_idx, len(target_row) - 1)]
                elif circular:
                    target_row = grid[0]
                    target = target_row[min(col_idx, len(target_row) - 1)]
            
            elif key == Qt.Key.Key_Left:
                if col_idx > 0:
                    target = grid[row_idx][col_idx - 1]
                elif circular and len(grid[row_idx]) > 1:
                    target = grid[row_idx][-1]
            
            elif key == Qt.Key.Key_Right:
                if col_idx < len(grid[row_idx]) - 1:
                    target = grid[row_idx][col_idx + 1]
                elif circular and len(grid[row_idx]) > 1:
                    target = grid[row_idx][0]
            
            if target:
                self._focus_target(target)
                return True
        
        return False
    
    def _handle_table_shortcuts(self, table, event) -> bool:
        """Handle table shortcuts"""
        key = event.key()
        modifiers = event.modifiers()
        row = table.currentRow()
        
        callbacks = self._table_callbacks.get(table, {})
        
        # F2 / Enter = Edit
        if key in (Qt.Key.Key_F2, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if 'edit' in callbacks:
                callbacks['edit']()
                return True
        
        # Delete = Delete
        if key == Qt.Key.Key_Delete:
            if 'delete' in callbacks:
                callbacks['delete']()
                return True
        
        # Ctrl+Up/Down
        if modifiers == Qt.KeyboardModifier.ControlModifier:
            if key == Qt.Key.Key_Up and 'focus_up' in callbacks:
                self._focus_target(callbacks['focus_up'])
                return True
            
            if key == Qt.Key.Key_Down and 'focus_down' in callbacks:
                self._focus_target(callbacks['focus_down'])
                return True
        
        # Up at row 0 = Focus up WITH MEMORY
        if key == Qt.Key.Key_Up and row == 0 and 'focus_up' in callbacks:
            target = callbacks['focus_up']
            
            # ✅ Smart memory: Balik ke widget terakhir sebelum ke table
            if self._focus_history:
                last_focus = self._focus_history[-1]
                # Cek apakah last focus masih di button row yang sama
                if last_focus and last_focus in self._navigation_map:
                    target = last_focus
            
            self._focus_target(target)
            return True
        
        # Down at last row = Focus down
        if key == Qt.Key.Key_Down and row == table.rowCount() - 1:
            if 'focus_down' in callbacks:
                self._focus_target(callbacks['focus_down'])
                return True
        
        return False
    
    def _handle_widget_navigation(self, widget, event) -> bool:
        """Handle widget navigation with memory support"""
        nav_dict = self._navigation_map[widget]
        key = event.key()
        
        if key not in nav_dict:
            return False
        
        target = nav_dict[key]
        
        # Check if memory navigation
        if isinstance(target, dict) and target.get('_memory_nav'):
            to_widget = target['target']
            self._focus_target(to_widget)
            return True
        
        # Normal navigation
        if callable(target):
            target()
        elif target is not None:
            self._focus_target(target)
        
        return True
    
    def _focus_target(self, target):
        """Focus target widget"""
        if callable(target):
            target()
        elif target is not None:
            target.setFocus()
            if isinstance(target, (QLineEdit, QTextEdit)) and hasattr(target, 'selectAll'):
                target.selectAll()
    
    # ========== HELPER METHODS ==========
    
    def handle_escape(self) -> bool:
        """Handle ESC - override in subclass"""
        self.close()
        return True
    
    def focus_table_first_row(self, table):
        """Focus table first row"""
        if table.rowCount() > 0:
            table.setFocus()
            table.selectRow(0)
    
    def focus_table_last_row(self, table):
        """Focus table last row"""
        if table.rowCount() > 0:
            table.setFocus()
            table.selectRow(table.rowCount() - 1)