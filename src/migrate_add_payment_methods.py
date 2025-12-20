"""
Migration: Add payment_methods table
=====================================
Run: python src/migrate_add_payment_methods.py
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import shutil

# Import DB_PATH dari config
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.paths import DB_PATH


def migrate():
    """Add payment_methods table untuk multi-payment support"""
    
    if not DB_PATH.exists():
        print("❌ Database tidak ada!")
        return
    
    # Backup dulu
    backup_folder = DB_PATH.parent / "backup"
    backup_folder.mkdir(exist_ok=True)
    
    backup_path = backup_folder / f"pos_backup_before_multipayment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy(DB_PATH, backup_path)
    print(f"✅ Backup: {backup_path}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Cek apakah tabel sudah ada
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='payment_methods'")
        if cursor.fetchone():
            print("ℹ️  Tabel payment_methods sudah ada")
            conn.close()
            return
        
        # Create payment_methods table
        cursor.execute("""
            CREATE TABLE payment_methods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaksi_id INTEGER NOT NULL,
                method TEXT NOT NULL,
                amount REAL NOT NULL,
                FOREIGN KEY(transaksi_id) REFERENCES transaksi(id) ON DELETE CASCADE
            )
        """)
        
        print("✅ Tabel payment_methods berhasil dibuat")
        
        # Migrate existing transactions (semua jadi cash)
        cursor.execute("SELECT id, total FROM transaksi")
        transactions = cursor.fetchall()
        
        for trans_id, total in transactions:
            cursor.execute(
                "INSERT INTO payment_methods (transaksi_id, method, amount) VALUES (?, 'cash', ?)",
                (trans_id, total)
            )
        
        print(f"✅ Migrasi {len(transactions)} transaksi lama (default: cash)")
        
        conn.commit()
        print("\n🎉 Migrasi selesai!")
        print("📊 Database siap untuk multi-payment!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("MIGRASI: Multi-Payment Method Support")
    print("=" * 60)
    migrate()