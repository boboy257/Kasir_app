"""
Centralized Paths Configuration
================================
Single source of truth untuk semua paths di aplikasi

✅ Benefits:
- No more scattered path definitions
- Easy to change folder structure
- Consistent across all modules
- Easy migration support
"""

import os
from pathlib import Path

# ========== ROOT DIRECTORY ==========
# Auto-detect root folder (2 levels up from this file)
CURRENT_FILE = Path(__file__).resolve()
ROOT_DIR = CURRENT_FILE.parent.parent.parent  # Kasir_app/

# ========== MAIN FOLDERS ==========
DATA_FOLDER = ROOT_DIR / "data"
RESOURCES_FOLDER = ROOT_DIR / "resources"

# ========== DATA SUBFOLDERS ==========
BACKUP_FOLDER = DATA_FOLDER / "backup"
EXPORT_FOLDER = DATA_FOLDER / "export"
LOGS_FOLDER = DATA_FOLDER / "logs"

# ========== OUTPUT FOLDERS ==========
STRUK_FOLDER = ROOT_DIR / "struk"
BARCODE_FOLDER = ROOT_DIR / "barcode"

# ========== FILES ==========
DB_PATH = DATA_FOLDER / "pos.db"
SETTINGS_FILE = DATA_FOLDER / "settings.json"

# ========== RESOURCES SUBFOLDERS ==========
STYLES_FOLDER = RESOURCES_FOLDER / "styles"
ICONS_FOLDER = RESOURCES_FOLDER / "icons"
IMAGES_FOLDER = RESOURCES_FOLDER / "images"

# ========== HELPER FUNCTIONS ==========

def ensure_folders_exist():
    """
    Pastikan semua folder yang dibutuhkan sudah ada.
    Dipanggil saat aplikasi start.
    """
    folders = [
        DATA_FOLDER,
        BACKUP_FOLDER,
        EXPORT_FOLDER,
        LOGS_FOLDER,
        STRUK_FOLDER,
        BARCODE_FOLDER,
        RESOURCES_FOLDER,
        STYLES_FOLDER,
        ICONS_FOLDER,
        IMAGES_FOLDER,
    ]
    
    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ All folders verified at: {ROOT_DIR}")


def migrate_old_folders():
    """
    Migrate dari struktur folder lama ke struktur baru.
    
    OLD STRUCTURE:
    - Kasir_app/export/  → data/export/
    - Kasir_app/backup/  → data/backup/
    
    SAFE: Tidak akan overwrite file yang sudah ada
    """
    import shutil
    
    print("🔄 Checking for old folder structure...")
    
    migrations = [
        (ROOT_DIR / "export", EXPORT_FOLDER),
        (ROOT_DIR / "backup", BACKUP_FOLDER),
    ]
    
    migrated_count = 0
    
    for old_path, new_path in migrations:
        if old_path.exists() and old_path != new_path:
            print(f"   📂 Found old folder: {old_path.name}/")
            
            # Ensure target exists
            new_path.mkdir(parents=True, exist_ok=True)
            
            # Move files (not folder)
            try:
                for item in old_path.iterdir():
                    target = new_path / item.name
                    
                    if not target.exists():
                        shutil.move(str(item), str(target))
                        print(f"      ✅ Moved: {item.name}")
                    else:
                        print(f"      ⏭️  Skipped: {item.name} (already exists)")
                
                # Remove empty old folder
                if not any(old_path.iterdir()):
                    old_path.rmdir()
                    print(f"      🗑️  Removed empty folder: {old_path.name}/")
                
                migrated_count += 1
                
            except Exception as e:
                print(f"      ⚠️  Error migrating {old_path.name}: {e}")
    
    if migrated_count > 0:
        print(f"\n✅ Migration completed: {migrated_count} folder(s) migrated")
    else:
        print("ℹ️  No old folders to migrate (already clean)")
    
    # Ensure all new folders exist
    ensure_folders_exist()


def get_backup_filename(prefix="backup_pos"):
    """Generate backup filename with timestamp"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.db"


def get_export_filename(prefix="export", extension="csv"):
    """Generate export filename with timestamp"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


# ========== PATH VALIDATION ==========

def validate_paths():
    """
    Validate semua paths sudah benar.
    Useful untuk debugging.
    
    Returns:
        bool: True if all OK
    """
    paths_to_check = {
        "ROOT_DIR": ROOT_DIR,
        "DATA_FOLDER": DATA_FOLDER,
        "DB_PATH": DB_PATH,
        "SETTINGS_FILE": SETTINGS_FILE,
        "BACKUP_FOLDER": BACKUP_FOLDER,
        "EXPORT_FOLDER": EXPORT_FOLDER,
        "STRUK_FOLDER": STRUK_FOLDER,
        "BARCODE_FOLDER": BARCODE_FOLDER,
    }
    
    print("\n📍 PATH VALIDATION:")
    print("=" * 70)
    
    all_ok = True
    
    for name, path in paths_to_check.items():
        exists = path.exists()
        is_file = path.is_file() if exists else False
        is_dir = path.is_dir() if exists else False
        
        if name in ["DB_PATH", "SETTINGS_FILE"]:
            # Files - OK if parent folder exists
            status = "✅" if path.parent.exists() else "❌"
            type_str = "file (parent OK)" if path.parent.exists() else "file (missing parent)"
        else:
            # Folders - OK if exists
            status = "✅" if exists else "⚠️ "
            type_str = "folder" if is_dir else "will be created"
        
        print(f"{status} {name:20s} [{type_str:20s}]: {path}")
        
        if not path.parent.exists():
            all_ok = False
    
    print("=" * 70)
    
    return all_ok


# ========== AUTO-RUN ON IMPORT (for debugging) ==========
if __name__ == "__main__":
    print("🔍 Paths Configuration Test")
    print("=" * 70)
    print(f"ROOT_DIR: {ROOT_DIR}")
    print(f"DATA_FOLDER: {DATA_FOLDER}")
    print(f"DB_PATH: {DB_PATH}")
    print(f"SETTINGS_FILE: {SETTINGS_FILE}")
    print("=" * 70)
    
    validate_paths()
    
    print("\n✅ paths.py is working correctly!")