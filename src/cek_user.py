import sys
import os
import sqlite3

# --- BAGIAN PENTING: IMPOR PATH DARI PUSAT ---
# Kita tambahkan folder project ke sistem agar bisa import modul 'src'
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir) # Folder Kasir_app
sys.path.append(current_dir)
sys.path.append(parent_dir)

try:
    # Coba ambil path database RESMI dari src/database.py
    # Ini menjamin kita melihat file yang SAMA PERSIS dengan aplikasi utama
    from src.database import DB_PATH
except ImportError:
    print("⚠️ Gagal mengimpor konfigurasi database.")
    print("Pastikan file ini berada di folder utama project (sejajar dengan main.py)")
    # Fallback manual jika import gagal (ke folder data di root)
    DB_PATH = os.path.join(parent_dir, "data", "pos.db")

def cek_isi_user():
    print(f"📂 Target Database: {DB_PATH}\n")
    
    if not os.path.exists(DB_PATH):
        print("❌ File database TIDAK DITEMUKAN di lokasi ini!")
        print("👉 Solusi: Jalankan 'python reset_data.py' dulu.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Cek apakah tabel user ada
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if not cursor.fetchone():
            print("❌ Tabel 'user' BELUM ADA.")
            return

        # Cek kolom role (untuk memastikan struktur database baru)
        cursor.execute("PRAGMA table_info(user)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'role' not in columns:
            print("❌ Tabel user ditemukan, tapi kolom 'role' TIDAK ADA.")
            print("👉 Solusi: Database Anda versi lama. Jalankan 'python reset_data.py' untuk upgrade.")
            return

        # Ambil data user
        cursor.execute("SELECT id, username, password, role FROM user")
        users = cursor.fetchall()
        
        print(f"✅ DATABASE VALID! Ditemukan {len(users)} user:")
        print("-" * 65)
        print(f"{'ID':<5} {'USERNAME':<15} {'ROLE':<10} {'PASSWORD (Hash)'}")
        print("-" * 65)
        
        for u in users:
            role_str = u[3] if u[3] else "NULL"
            print(f"{u[0]:<5} {u[1]:<15} {role_str:<10} {u[2][:10]}...")
            
    except Exception as e:
        print(f"Error tak terduga: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    cek_isi_user()