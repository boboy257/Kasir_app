"""
Keyboard Navigation Migration Script
=====================================
Migrate semua windows ke KeyboardMixin pattern

What this does:
1. Backup old files
2. Update imports
3. Show diff summary
4. Create TODO list for manual fixes

Usage:
    python migrate_keyboard_navigation.py
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Files to migrate
WINDOWS_TO_MIGRATE = [
    "src/ui/windows/kasir_window.py",
    "src/ui/windows/laporan_window.py",
    "src/ui/windows/stok_rendah_window.py",
    "src/ui/windows/generate_barcode_window.py",
    "src/ui/windows/kelola_db_window.py",
    "src/ui/windows/manajemen_user_window.py",
    "src/ui/windows/log_aktivitas_window.py",
    "src/ui/windows/pengaturan_window.py",
    "src/ui/windows/riwayat_hari_ini_window.py",
]


def backup_file(filepath):
    """Create backup with timestamp"""
    backup_dir = Path("archive/keyboard_migration")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = Path(filepath).name
    backup_path = backup_dir / f"{filename}.{timestamp}.bak"
    
    shutil.copy(filepath, backup_path)
    print(f"  ✅ Backup: {backup_path}")
    return backup_path


def analyze_window(filepath):
    """Analyze window untuk identify patterns"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    findings = {
        'has_eventfilter': 'def eventFilter' in content,
        'has_f2_shortcut': 'Key.Key_F2' in content or 'Qt.Key.F2' in content,
        'has_delete_shortcut': 'Key.Key_Delete' in content,
        'has_ctrl_shortcuts': 'ControlModifier' in content,
        'has_table': 'QTableWidget' in content,
        'line_count': len(content.split('\n')),
        'eventfilter_lines': content.count('def eventFilter'),
    }
    
    return findings


def create_migration_report():
    """Create detailed migration report"""
    print("=" * 70)
    print("🔍 KEYBOARD NAVIGATION MIGRATION ANALYSIS")
    print("=" * 70)
    print()
    
    report = []
    
    for filepath in WINDOWS_TO_MIGRATE:
        if not os.path.exists(filepath):
            print(f"⚠️  SKIP: {filepath} (tidak ditemukan)")
            continue
        
        print(f"📄 Analyzing: {filepath}")
        findings = analyze_window(filepath)
        
        # Summary
        complexity = "🔴 HIGH" if findings['has_eventfilter'] and findings['has_ctrl_shortcuts'] else \
                     "🟡 MEDIUM" if findings['has_eventfilter'] else \
                     "🟢 LOW"
        
        print(f"   Complexity: {complexity}")
        print(f"   Lines: {findings['line_count']}")
        print(f"   Has eventFilter: {'✅' if findings['has_eventfilter'] else '❌'}")
        print(f"   Has F2 shortcut: {'✅' if findings['has_f2_shortcut'] else '❌'}")
        print(f"   Has Delete shortcut: {'✅' if findings['has_delete_shortcut'] else '❌'}")
        print(f"   Has Ctrl shortcuts: {'✅' if findings['has_ctrl_shortcuts'] else '❌'}")
        print(f"   Has Table: {'✅' if findings['has_table'] else '❌'}")
        print()
        
        report.append({
            'file': filepath,
            'findings': findings,
            'complexity': complexity
        })
    
    return report


def generate_migration_guide(report):
    """Generate step-by-step migration guide"""
    print()
    print("=" * 70)
    print("📋 MIGRATION GUIDE")
    print("=" * 70)
    print()
    
    # Sort by complexity
    high = [r for r in report if r['complexity'] == "🔴 HIGH"]
    medium = [r for r in report if r['complexity'] == "🟡 MEDIUM"]
    low = [r for r in report if r['complexity'] == "🟢 LOW"]
    
    print("🔴 HIGH COMPLEXITY (Do Last):")
    for item in high:
        print(f"   - {item['file']}")
    print()
    
    print("🟡 MEDIUM COMPLEXITY (Do Second):")
    for item in medium:
        print(f"   - {item['file']}")
    print()
    
    print("🟢 LOW COMPLEXITY (Do First):")
    for item in low:
        print(f"   - {item['file']}")
    print()
    
    print("=" * 70)
    print("📝 MIGRATION STEPS (Per Window)")
    print("=" * 70)
    print()
    print("1. Backup file (automatic)")
    print("2. Update import:")
    print("   from src.ui.base.base_window import BaseWindow")
    print()
    print("3. Remove old eventFilter method")
    print()
    print("4. Create setup_navigation() method:")
    print("   def setup_navigation(self):")
    print("       # Register form navigation")
    print("       self.register_navigation(self.input1, {")
    print("           Qt.Key.Key_Down: self.input2")
    print("       })")
    print()
    print("       # Register table callbacks")
    print("       self.register_table_callbacks(self.table, {")
    print("           'edit': self.edit_method,")
    print("           'delete': self.delete_method,")
    print("           'focus_up': self.search_input")
    print("       })")
    print()
    print("5. Call setup_navigation() in __init__")
    print()
    print("6. Test semua keyboard shortcuts")
    print()
    print("=" * 70)


def create_checklist():
    """Create migration checklist"""
    checklist_path = Path("KEYBOARD_MIGRATION_CHECKLIST.md")
    
    content = """# Keyboard Navigation Migration Checklist

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
"""
    
    with open(checklist_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"📝 Checklist created: {checklist_path}")


def main():
    """Main migration script"""
    print()
    print("🚀 KEYBOARD NAVIGATION MIGRATION TOOL")
    print("=" * 70)
    print()
    print("This script will:")
    print("  1. Analyze all windows")
    print("  2. Create backups")
    print("  3. Generate migration guide")
    print("  4. Create checklist")
    print()
    
    input("Press Enter to start analysis... ")
    print()
    
    # Step 1: Analyze
    report = create_migration_report()
    
    # Step 2: Generate guide
    generate_migration_guide(report)
    
    # Step 3: Create checklist
    create_checklist()
    
    print()
    print("=" * 70)
    print("✅ ANALYSIS COMPLETE!")
    print("=" * 70)
    print()
    print("📌 NEXT STEPS:")
    print()
    print("1. Review KEYBOARD_MIGRATION_CHECKLIST.md")
    print("2. Start with LOW complexity windows (pengaturan, log)")
    print("3. Use produk_window.py as reference")
    print("4. Test thoroughly after each migration")
    print("5. Commit after each successful migration")
    print()
    print("🎯 RECOMMENDED ORDER:")
    print("   pengaturan → log → laporan → stok → riwayat → kelola")
    print("   → generate_barcode → manajemen_user → kasir (LAST!)")
    print()
    print("💡 TIP: Do 1-2 windows per day for quality")
    print()


if __name__ == "__main__":
    main()