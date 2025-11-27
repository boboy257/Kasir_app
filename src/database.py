import sqlite3
from pathlib import Path
import shutil
from datetime import datetime, timezone
import csv
import hashlib
import os
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont

DB_PATH = Path("data/pos.db")

def create_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    # Tabel produk
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produk (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT UNIQUE,
            nama TEXT NOT NULL,
            harga REAL NOT NULL,
            stok INTEGER DEFAULT 0
        )
    """)

    # Tabel transaksi
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT NOT NULL,
            total REAL NOT NULL
        )
    """)

    # Tabel user
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Tabel detail transaksi
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detail_transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaksi_id INTEGER,
            produk_nama TEXT NOT NULL,
            jumlah INTEGER NOT NULL,
            harga REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY(transaksi_id) REFERENCES transaksi(id)
        )
    """)

    # Tabel log aktivitas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS log_aktivitas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            aktivitas TEXT NOT NULL,
            tanggal TEXT NOT NULL,
            detail TEXT
        )
    """)

    conn.commit()
    conn.close()

def tambah_produk(barcode, nama, harga, stok=0):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO produk (barcode, nama, harga, stok)
        VALUES (?, ?, ?, ?)
    """, (barcode, nama, harga, stok))
    conn.commit()
    conn.close()

def cari_produk_dari_barcode(barcode):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nama, harga FROM produk WHERE barcode = ?", (barcode,))
    produk = cursor.fetchone()
    conn.close()
    return produk

def semua_produk():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, barcode, nama, harga, stok FROM produk")
    produk = cursor.fetchall()
    conn.close()
    return produk

# === TAMBAHAN UNTUK KELOLA DATABASE ===

def backup_database():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = Path(f"data/backup_pos_{timestamp}.db")
    backup_path.parent.mkdir(exist_ok=True)
    shutil.copy(DB_PATH, backup_path)
    return backup_path

def restore_database(backup_path):
    shutil.copy(backup_path, DB_PATH)
    print(f"Database berhasil dipulihkan dari {backup_path}")

def export_produk_ke_csv():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, barcode, nama, harga, stok FROM produk")
    rows = cursor.fetchall()
    conn.close()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = Path(f"data/produk_{timestamp}.csv")
    csv_path.parent.mkdir(exist_ok=True)

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["id", "barcode", "nama", "harga", "stok"])
        writer.writerows(rows)

    return csv_path

def import_produk_dari_csv(csv_path):
    conn = create_connection()
    cursor = conn.cursor()

    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cursor.execute("""
                INSERT OR REPLACE INTO produk (id, barcode, nama, harga, stok)
                VALUES (?, ?, ?, ?)
            """, (int(row["id"]), row["barcode"], row["nama"], float(row["harga"]), int(row["stok"])))

    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password menggunakan SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def tambah_user(username, password):
    """Tambah user baru ke database"""
    conn = create_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    try:
        cursor.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        return True
    except Exception:
        conn.close()
        return False

def cek_login(username, password):
    """Cek apakah username dan password benar"""
    conn = create_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    cursor.execute("SELECT * FROM user WHERE username = ? AND password = ?", (username, hashed_password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def buat_user_default():
    """Buat user default jika belum ada user sama sekali"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM user")
    count = cursor.fetchone()[0]
    conn.close()
    
    if count == 0:
        # Buat user default: username=admin, password=admin
        tambah_user("admin", "admin")
        print("User default dibuat: username=admin, password=admin")

def semua_produk():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, barcode, nama, harga, stok FROM produk")
    produk = cursor.fetchall()
    conn.close()
    return produk

def cari_produk_by_id(id_produk):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, barcode, nama, harga, stok FROM produk WHERE id = ?", (id_produk,))
    produk = cursor.fetchone()
    conn.close()
    return produk

def update_produk(id_produk, barcode, nama, harga, stok):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE produk 
        SET barcode = ?, nama = ?, harga = ?, stok = ? 
        WHERE id = ?
    """, (barcode, nama, harga, stok, id_produk))
    conn.commit()
    conn.close()

def hapus_produk(id_produk):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produk WHERE id = ?", (id_produk,))
    conn.commit()
    conn.close()

def update_stok_produk(id_produk, stok_baru):
    """Update stok produk berdasarkan ID"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE produk SET stok = ? WHERE id = ?", (stok_baru, id_produk))
    conn.commit()
    conn.close()

def backup_database_otomatis():
    """Backup database otomatis saat aplikasi dibuka"""
    # import os  # Sudah diimport di awal file
    from datetime import datetime  # Sudah diimport di awal file
    
    # Cek apakah file database ada
    if not DB_PATH.exists():
        print("Database belum ada, tidak perlu backup.")
        return
    
    # Buat folder backup jika belum ada
    backup_folder = Path("data/backup")
    backup_folder.mkdir(exist_ok=True)
    
    # Nama file backup dengan timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_folder / f"pos_backup_{timestamp}.db"
    
    # Copy database ke folder backup
    shutil.copy(DB_PATH, backup_path)
    
    print(f"Backup otomatis dibuat: {backup_path}")
    return backup_path

def backup_database_harian():
    """Backup database harian (hanya satu backup per hari)"""
    # import os  # Sudah diimport di awal file
    from datetime import datetime  # Sudah diimport di awal file
    
    # Cek apakah file database ada
    if not DB_PATH.exists():
        print("Database belum ada, tidak perlu backup.")
        return
    
    # Buat folder backup jika belum ada
    backup_folder = Path("data/backup")
    backup_folder.mkdir(exist_ok=True)
    
    # Nama file backup dengan tanggal hari ini
    tanggal_hari_ini = datetime.now().strftime("%Y%m%d")
    backup_path = backup_folder / f"pos_backup_{tanggal_hari_ini}.db"
    
    # Cek apakah backup hari ini sudah ada
    if backup_path.exists():
        print(f"Backup hari ini sudah ada: {backup_path}")
        return
    
    # Copy database ke folder backup
    shutil.copy(DB_PATH, backup_path)
    
    print(f"Backup harian dibuat: {backup_path}")
    return backup_path

def cek_produk_stok_rendah(batas_stok=5):
    """Cek produk dengan stok di bawah batas tertentu"""
    conn = create_connection()
    cursor = conn.cursor()
    
    # Query untuk ambil produk dengan stok rendah
    cursor.execute("""
        SELECT id, barcode, nama, stok 
        FROM produk 
        WHERE stok < ? 
        ORDER BY stok ASC
    """, (batas_stok,))
    hasil = cursor.fetchall()
    conn.close()
    
    return hasil

def tampilkan_notifikasi_stok_rendah():
    """Tampilkan notifikasi jika ada produk dengan stok rendah"""
    from PyQt6.QtWidgets import QMessageBox
    
    produk_rendah = cek_produk_stok_rendah(batas_stok=5)
    
    if produk_rendah:
        # Buat pesan untuk semua produk dengan stok rendah
        pesan = "Produk dengan stok rendah:\n\n"
        for id_produk, barcode, nama, stok in produk_rendah:
            pesan += f"- {nama} (Barcode: {barcode}): {stok} pcs\n"
        
        pesan += f"\nTotal: {len(produk_rendah)} produk"
        
        # Tampilkan pesan peringatan
        msg = QMessageBox()
        msg.setWindowTitle("Peringatan Stok Rendah")
        msg.setText(pesan)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.exec()
    else:
        print("Tidak ada produk dengan stok rendah.")

def generate_barcode_gambar(barcode_value, nama_produk, output_path):
    """Generate barcode sebagai gambar PNG"""
    # from barcode import Code128  # Sudah diimport di awal file
    # from barcode.writer import ImageWriter  # Sudah diimport di awal file
    # import os  # Sudah diimport di awal file
    
    # Buat folder barcode jika belum ada
    barcode_folder = os.path.dirname(output_path)
    os.makedirs(barcode_folder, exist_ok=True)
    
    # Buat barcode
    barcode = Code128(barcode_value, writer=ImageWriter())
    
    # Generate barcode ke file
    barcode_path = barcode.save(output_path)
    
    # Tambahkan nama produk di bawah barcode
    # from PIL import Image, ImageDraw, ImageFont  # Sudah diimport di awal file
    
    # Buka gambar barcode
    img = Image.open(barcode_path)
    
    # Buat area baru dengan ruang untuk nama produk
    new_height = img.height + 40  # Tambahkan 40 pixel untuk teks
    new_img = Image.new('RGB', (img.width, new_height), 'white')
    new_img.paste(img, (0, 0))
    
    # Tambahkan nama produk
    draw = ImageDraw.Draw(new_img)
    try:
        # Gunakan font default
        font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Tengahkan teks nama produk
    bbox = draw.textbbox((0, 0), nama_produk, font=font)
    text_width = bbox[2] - bbox[0]
    x = (img.width - text_width) // 2
    y = img.height + 10
    
    draw.text((x, y), nama_produk, fill='black', font=font)
    
    # Simpan gambar baru
    new_img.save(barcode_path)
    
    return barcode_path

def generate_semua_barcode_gambar():
    """Generate barcode untuk semua produk"""
    import os
    from datetime import datetime
    
    # Ambil semua produk dari database
    produk_list = semua_produk()
    
    if not produk_list:
        print("Tidak ada produk untuk generate barcode.")
        return []
    
    # Buat folder barcode jika belum ada
    barcode_folder = "barcode"
    os.makedirs(barcode_folder, exist_ok=True)
    
    hasil = []
    
    for id_produk, barcode, nama, harga, stok in produk_list:
        if barcode:  # Hanya generate jika ada barcode
            # Nama file: barcode_nama_produk.png
            filename = f"{barcode}_{nama.replace(' ', '_')}.png"
            output_path = os.path.join(barcode_folder, filename)
            
            try:
                barcode_path = generate_barcode_gambar(barcode, nama, output_path)
                hasil.append(barcode_path)
                print(f"Barcode dibuat: {barcode_path}")
            except Exception as e:
                print(f"Gagal generate barcode untuk {nama}: {str(e)}")
    
    return hasil

def semua_user():
    """Ambil semua user dari database"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM user")
    hasil = cursor.fetchall()
    conn.close()
    return hasil

def tambah_user_baru(username, password):
    """Tambah user baru ke database"""
    conn = create_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    try:
        cursor.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        return True
    except Exception:
        conn.close()
        return False

def update_user(id_user, username_baru, password_baru=None):
    """Update user (username dan/atau password)"""
    conn = create_connection()
    cursor = conn.cursor()
    
    if password_baru:
        hashed_password = hash_password(password_baru)
        cursor.execute("UPDATE user SET username = ?, password = ? WHERE id = ?", 
                      (username_baru, hashed_password, id_user))
    else:
        cursor.execute("UPDATE user SET username = ? WHERE id = ?", (username_baru, id_user))
    
    conn.commit()
    conn.close()

def hapus_user(id_user):
    """Hapus user dari database"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user WHERE id = ?", (id_user,))
    conn.commit()
    conn.close()

def cek_username_sudah_ada(username, id_user_kecuali=None):
    """Cek apakah username sudah ada (untuk validasi update)"""
    conn = create_connection()
    cursor = conn.cursor()
    
    if id_user_kecuali:
        cursor.execute("SELECT COUNT(*) FROM user WHERE username = ? AND id != ?", (username, id_user_kecuali))
    else:
        cursor.execute("SELECT COUNT(*) FROM user WHERE username = ?", (username,))
    
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def log_aktivitas_pengguna(username, aktivitas, detail=None):
    """Log aktivitas pengguna ke database"""
    # from datetime import datetime  # Sudah diimport di awal file
    
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO log_aktivitas (username, aktivitas, tanggal, detail)
        VALUES (?, ?, ?, ?)
    """, (username, aktivitas, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), detail))
    
    conn.commit()
    conn.close()

def ambil_log_aktivitas(username=None, limit=50):
    """Ambil log aktivitas (semua atau berdasarkan user)"""
    conn = create_connection()
    cursor = conn.cursor()
    
    if username:
        cursor.execute("""
            SELECT username, aktivitas, tanggal, detail
            FROM log_aktivitas
            WHERE username = ?
            ORDER BY tanggal DESC
            LIMIT ?
        """, (username, limit))
    else:
        cursor.execute("""
            SELECT username, aktivitas, tanggal, detail
            FROM log_aktivitas
            ORDER BY tanggal DESC
            LIMIT ?
        """, (limit,))
    
    hasil = cursor.fetchall()
    conn.close()
    return hasil

def tambah_produk_dengan_log(barcode, nama, harga, stok, username):
    """Tambah produk dan log aktivitas"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO produk (barcode, nama, harga, stok)
        VALUES (?, ?, ?, ?)
    """, (barcode, nama, harga, stok))
    conn.commit()
    conn.close()
    
    # Log aktivitas
    log_aktivitas_pengguna(username, "Tambah Produk", f"Barcode: {barcode}, Nama: {nama}")

def update_produk_dengan_log(id_produk, barcode, nama, harga, stok, username):
    """Update produk dan log aktivitas"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE produk 
        SET barcode = ?, nama = ?, harga = ?, stok = ? 
        WHERE id = ?
    """, (barcode, nama, harga, stok, id_produk))
    conn.commit()
    conn.close()
    
    # Log aktivitas
    log_aktivitas_pengguna(username, "Edit Produk", f"ID: {id_produk}, Nama: {nama}")

def hapus_produk_dengan_log(id_produk, username):
    """Hapus produk dan log aktivitas"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produk WHERE id = ?", (id_produk,))
    conn.commit()
    conn.close()
    
    # Log aktivitas
    log_aktivitas_pengguna(username, "Hapus Produk", f"ID: {id_produk}")