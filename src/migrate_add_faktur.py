"""Migrasi: Tambah kolom no_faktur ke tabel transaksi"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = Path(os.path.join(CURRENT_DIR, "data", "pos.db"))

def migrate():
    if not DB_PATH.exists():
        print("❌ Database tidak ada")
        return
    
    # Backup dulu
    backup_path = DB_PATH.parent / f"pos_backup_before_faktur_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    import shutil
    shutil.copy(DB_PATH, backup_path)
    print(f"✅ Backup: {backup_path}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Cek apakah kolom sudah ada
        cursor.execute("PRAGMA table_info(transaksi)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'no_faktur' in columns:
            print("ℹ️  Kolom no_faktur sudah ada")
        else:
            # Tambah kolom
            cursor.execute("ALTER TABLE transaksi ADD COLUMN no_faktur TEXT")
            print("✅ Kolom no_faktur ditambahkan")
            
            # Generate nomor faktur untuk transaksi lama
            cursor.execute("SELECT id, tanggal FROM transaksi WHERE no_faktur IS NULL")
            old_transactions = cursor.fetchall()
            
            for trans_id, tanggal in old_transactions:
                # Format: INV-[timestamp]-[id]
                fake_faktur = f"INV-OLD-{trans_id:05d}"
                cursor.execute("UPDATE transaksi SET no_faktur = ? WHERE id = ?", (fake_faktur, trans_id))
            
            print(f"✅ Generate nomor faktur untuk {len(old_transactions)} transaksi lama")
        
        conn.commit()
        print("\n🎉 Migrasi selesai!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()