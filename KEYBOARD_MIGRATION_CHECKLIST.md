# Keyboard Navigation Migration Checklist

## 🎯 Goal
Migrate all windows to use KeyboardMixin for consistent navigation.

## ✅ Completed
- [x] Create KeyboardMixin (`src/ui/base/keyboard_mixin.py`)
- [x] Update BaseWindow to use mixin
- [x] Refactor produk_window.py as reference
- [x] Create SmartTable widget

## 📋 Windows to Migrate

### 🟢 Low Complexity (Start Here)
- [ ] pengaturan_window.py
- [ ] log_aktivitas_window.py

### 🟡 Medium Complexity
- [ ] laporan_window.py
- [ ] stok_rendah_window.py
- [ ] riwayat_hari_ini_window.py
- [ ] kelola_db_window.py

### 🔴 High Complexity (Do Last)
- [ ] kasir_window.py (most complex!)
- [ ] generate_barcode_window.py
- [ ] manajemen_user_window.py

## 📝 Migration Template

For each window:

1. **Backup**
   ```bash
   # Automatic backup created
   ```

2. **Update Import**
   ```python
   from src.ui.base.base_window import BaseWindow
   ```

3. **Remove**
   - `def eventFilter()` method
   - Manual keyboard handling code

4. **Add setup_navigation()**
   ```python
   def setup_navigation(self):
       # Form navigation
       self.register_navigation(widget, {
           Qt.Key.Key_Down: next_widget
       })
       
       # Table shortcuts
       self.register_table_callbacks(self.table, {
           'edit': self.edit_method,
           'delete': self.delete_method,
           'focus_up': self.search_input
       })
   ```

5. **Call in __init__**
   ```python
   def __init__(self):
       super().__init__()
       self.setup_ui()
       self.setup_navigation()  # Add this!
   ```

6. **Test**
   - [ ] Arrow navigation works
   - [ ] F2 edit works
   - [ ] Delete works
   - [ ] Ctrl+Up/Down works
   - [ ] Ctrl+S/N/F works
   - [ ] ESC works

## 🎉 Benefits After Migration

- ✅ Consistent keyboard shortcuts across all windows
- ✅ Less code (100+ lines → 20 lines)
- ✅ Easier to maintain
- ✅ Self-documenting navigation
- ✅ Easy to add new shortcuts

## 📚 Reference

See `produk_window.py` for complete example.
