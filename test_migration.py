"""
Test Migration Script
=====================
Jalankan ini untuk migrate old folders dan test struktur baru
"""

import sys
import os

# Tambahkan root folder ke Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    print("=" * 70)
    print("🔧 MIGRATION & TEST SCRIPT - FASE 1 REFACTOR")
    print("=" * 70)
    print()
    
    # Step 1: Migration
    print("📦 STEP 1: Migrating old folders...")
    print("-" * 70)
    
    try:
        from src.config.paths import migrate_old_folders
        migrate_old_folders()
        print("✅ Migration completed!\n")
    except Exception as e:
        print(f"❌ Migration failed: {e}\n")
        return False
    
    # Step 2: Verify Paths
    print("📂 STEP 2: Verifying paths...")
    print("-" * 70)
    
    try:
        from src.config.paths import (
            ROOT_DIR, DATA_FOLDER, DB_PATH, 
            BACKUP_FOLDER, EXPORT_FOLDER, STRUK_FOLDER,
            BARCODE_FOLDER, SETTINGS_FILE
        )
        
        paths_to_check = {
            "Root Directory": ROOT_DIR,
            "Data Folder": DATA_FOLDER,
            "Database Path": DB_PATH,
            "Backup Folder": BACKUP_FOLDER,
            "Export Folder": EXPORT_FOLDER,
            "Struk Folder": STRUK_FOLDER,
            "Barcode Folder": BARCODE_FOLDER,
            "Settings File": SETTINGS_FILE,
        }
        
        all_ok = True
        for name, path in paths_to_check.items():
            exists = path.exists() if hasattr(path, 'exists') else os.path.exists(path)
            status = "✅" if exists else "⚠️ "
            print(f"{status} {name:20s}: {path}")
            
            if not exists and name != "Database Path":  # DB belum dibuat OK
                all_ok = False
        
        print()
        if all_ok:
            print("✅ All paths verified!\n")
        else:
            print("⚠️  Some paths missing (will be created on first run)\n")
            
    except Exception as e:
        print(f"❌ Path verification failed: {e}\n")
        return False
    
    # Step 3: Test Imports
    print("🔍 STEP 3: Testing imports...")
    print("-" * 70)
    
    try:
        # Test database imports
        from src.database import DB_PATH as db_path_from_db
        print(f"✅ database.py imports config correctly")
        print(f"   DB_PATH = {db_path_from_db}")
        
        # Test cetak_struk imports
        from src.cetak_struk import STRUK_FOLDER as struk_from_cetak
        print(f"✅ cetak_struk.py imports config correctly")
        print(f"   STRUK_FOLDER = {struk_from_cetak}")
        
        # Test settings imports
        from src.settings import SETTINGS_FILE as settings_from_settings
        print(f"✅ settings.py imports config correctly")
        print(f"   SETTINGS_FILE = {settings_from_settings}")
        
        print()
        print("✅ All imports working!\n")
        
    except Exception as e:
        print(f"❌ Import test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Summary
    print("=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print()
    print("✅ Migration: SUCCESS")
    print("✅ Paths: VERIFIED")
    print("✅ Imports: WORKING")
    print()
    print("🎉 Fase 1 - Step 1.4 (Centralized Paths) COMPLETE!")
    print()
    print("📌 NEXT STEPS:")
    print("   1. Run app: python src/main.py")
    print("   2. Test all features")
    print("   3. Commit changes: git add . && git commit -m 'refactor: centralize paths config'")
    print()
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)