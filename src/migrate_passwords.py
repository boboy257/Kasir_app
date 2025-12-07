import sqlite3
import bcrypt
import os

# Lokasi Database
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
DB_PATH = os.path.join(ROOT_DIR, "data", "pos.db")

def migrate_passwords():
    if not os.path.exists(DB_PATH):
        print("❌ Database tidak ditemukan! Pastikan Anda sudah pernah menjalankan aplikasi.")
        return

    print(f"📂 Mengakses Database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 1. Ambil semua user
        cursor.execute("SELECT id, username FROM user")
        users = cursor.fetchall()
        
        print(f"itemukan {len(users)} user untuk dimigrasi ke bcrypt...")

        # 2. Update password masing-masing
        for user_id, username in users:
            # Kita reset password mereka ke default sesuai username agar aman
            # Admin -> 'admin', Kasir -> 'kasir', User lain -> '123456'
            
            new_pass_plain = "123456" # Default untuk user lain
            if username == "admin":
                new_pass_plain = "admin"
            elif username == "kasir":
                new_pass_plain = "kasir"
            
            # Hash dengan BCRYPT
            salt = bcrypt.gensalt()
            hashed_bytes = bcrypt.hashpw(new_pass_plain.encode('utf-8'), salt)
            hashed_str = hashed_bytes.decode('utf-8')
            
            cursor.execute("UPDATE user SET password = ? WHERE id = ?", (hashed_str, user_id))
            print(f"✅ User '{username}' di-reset passwordnya menjadi: '{new_pass_plain}' (Terenkripsi)")

        conn.commit()
        print("\n🎉 SUKSES! Semua password telah dimigrasi ke sistem keamanan tinggi (bcrypt).")
        print("👉 Silakan login dengan password default di atas.")

    except Exception as e:
        print(f"❌ Terjadi kesalahan: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_passwords()