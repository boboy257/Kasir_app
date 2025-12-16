"""
Smart Table Widget
==================
Enhanced QTableWidget dengan smart defaults & konsistensi

Features:
- Consistent styling
- Optimal row height
- Alternating row colors
- Selection behavior
- Focus styling
- Easy column configuration
"""

from PyQt6.QtWidgets import QTableWidget, QAbstractItemView, QHeaderView
from PyQt6.QtCore import Qt


class SmartTable(QTableWidget):
    """
    Enhanced table dengan smart defaults
    
    Usage:
        # Basic usage
        table = SmartTable(0, 5)
        table.setHorizontalHeaderLabels(["ID", "Name", "Price", "Stock", "Actions"])
        
        # Hide column
        table.setColumnHidden(0, True)
        
        # Stretch column
        table.stretch_column(1)  # Name column stretches
        
        # Fixed width column
        table.set_column_width(2, 120)  # Price column fixed 120px
    """
    
    def __init__(self, rows=0, columns=0, parent=None):
        super().__init__(rows, columns, parent)
        self.setup_defaults()
    
    def setup_defaults(self):
        """Setup default behavior & styling"""
        
        # ========== BEHAVIOR ==========
        # Select entire rows (not individual cells)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        # No editing (read-only by default)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        # Single selection (can be changed to Multi if needed)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        
        # Enable alternating row colors
        self.setAlternatingRowColors(True)
        
        # Hide vertical header (row numbers)
        self.verticalHeader().setVisible(False)
        
        # ========== DIMENSIONS ==========
        # Optimal row height (not too cramped, not too spacious)
        self.verticalHeader().setDefaultSectionSize(40)
        
        # Header slightly taller
        self.horizontalHeader().setFixedHeight(35)
        
        # ========== STYLING ==========
        self.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E1E;
                alternate-background-color: #252525;
                gridline-color: #333;
                border: 1px solid #333;
                border-radius: 5px;
                color: #e0e0e0;
                selection-background-color: #2196F3;
                selection-color: white;
            }
            
            QTableWidget:focus {
                border: 2px solid #2196F3;
            }
            
            QTableWidget::item {
                padding: 5px;
            }
            
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            
            QTableWidget::item:hover {
                background-color: #333;
            }
            
            QHeaderView::section {
                background-color: #252525;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                border-bottom: 2px solid #2196F3;
            }
            
            QHeaderView::section:hover {
                background-color: #333;
            }
            
            QScrollBar:vertical {
                background-color: #1E1E1E;
                width: 12px;
                border: none;
            }
            
            QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #666;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
    
    # ========== CONVENIENCE METHODS ==========
    
    def stretch_column(self, column_index):
        """Make column stretch to fill available space"""
        self.horizontalHeader().setSectionResizeMode(
            column_index, QHeaderView.ResizeMode.Stretch
        )
    
    def set_column_width(self, column_index, width):
        """Set fixed column width"""
        self.setColumnWidth(column_index, width)
    
    def resize_columns_to_contents(self):
        """Auto-resize all columns to fit content"""
        for col in range(self.columnCount()):
            self.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeMode.ResizeToContents
            )
    
    def enable_editing(self):
        """Enable cell editing"""
        self.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked | 
            QAbstractItemView.EditTrigger.EditKeyPressed
        )
    
    def enable_multi_selection(self):
        """Enable multi-row selection"""
        self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
    
    def clear_table(self):
        """Clear all rows (keep columns)"""
        self.setRowCount(0)
    
    def get_selected_row_data(self):
        """
        Get data from selected row as list
        
        Returns:
            list: List of cell texts, or None if no selection
        """
        row = self.currentRow()
        if row < 0:
            return None
        
        data = []
        for col in range(self.columnCount()):
            item = self.item(row, col)
            data.append(item.text() if item else "")
        
        return data
    
    def get_all_data(self):
        """
        Get all table data as list of lists
        
        Returns:
            list: List of rows, each row is list of cell texts
        """
        data = []
        for row in range(self.rowCount()):
            row_data = []
            for col in range(self.columnCount()):
                item = self.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        
        return data
    
    def focus_first_row(self):
        """Focus and select first row"""
        if self.rowCount() > 0:
            self.setFocus()
            self.selectRow(0)
    
    def focus_last_row(self):
        """Focus and select last row"""
        if self.rowCount() > 0:
            self.setFocus()
            self.selectRow(self.rowCount() - 1)


# ========== EXAMPLE USAGE ==========

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
    import sys
    
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("SmartTable Demo")
    window.setGeometry(100, 100, 800, 600)
    
    central = QWidget()
    layout = QVBoxLayout(central)
    
    # Create smart table
    table = SmartTable(0, 5)
    table.setHorizontalHeaderLabels(["ID", "Product", "Price", "Stock", "Status"])
    
    # Hide ID column
    table.setColumnHidden(0, True)
    
    # Product column stretches
    table.stretch_column(1)
    
    # Fixed widths for others
    table.set_column_width(2, 120)
    table.set_column_width(3, 80)
    table.set_column_width(4, 100)
    
    # Add sample data
    from PyQt6.QtWidgets import QTableWidgetItem
    
    products = [
        ("1", "Indomie Goreng", "Rp 3.500", "100", "✅ Ready"),
        ("2", "Aqua 600ml", "Rp 4.000", "50", "✅ Ready"),
        ("3", "Minyak Goreng", "Rp 18.000", "3", "⚠️ Low"),
        ("4", "Gula Pasir", "Rp 16.000", "0", "❌ Empty"),
    ]
    
    for row_data in products:
        row = table.rowCount()
        table.insertRow(row)
        for col, value in enumerate(row_data):
            table.setItem(row, col, QTableWidgetItem(value))
    
    layout.addWidget(table)
    window.setCentralWidget(central)
    window.show()
    
    sys.exit(app.exec())