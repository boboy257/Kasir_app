import sqlite3
from pathlib import Path
import shutil
from datetime import datetime
import csv
import hashlib
import os
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
DB_PATH = Path(os.path.join(ROOT_DIR, "data", "pos.db"))
print(f"DATABASE PATH: {DB_PATH}")

def create_connection():
    # --- PERBAIKAN: Cek folder dulu sebelum connect ---
    # Ambil nama folder dari path database (yaitu folder "data")
    folder_database = os.path.dirname(DB_PATH)
    
    # Jika foldernya tidak ada, buat folder baru!
    if not os.path.exists(folder_database):
        os.makedirs(folder_database)
    # --------------------------------------------------

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
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'kasir'
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

# === [UPDATE PENTING] Fungsi ini diubah agar mengembalikan ID dan Stok juga ===
def cari_produk_dari_barcode(barcode):
    conn = create_connection()
    cursor = conn.cursor()
    # KITA UBAH QUERY INI: Ambil id dan stok juga
    cursor.execute("SELECT id, nama, harga, stok FROM produk WHERE barcode = ?", (barcode,))
    produk = cursor.fetchone()
    conn.close()
    return produk # Mengembalikan (id, nama, harga, stok)

# === [FITUR BARU] Fungsi pencarian manual ===
def cari_produk_by_nama_partial(keyword):
    """Mencari produk berdasarkan potongan nama (mirip LIKE di SQL)"""
    conn = create_connection()
    cursor = conn.cursor()
    param = f"%{keyword}%"
    cursor.execute("""
        SELECT id, barcode, nama, harga, stok 
        FROM produk 
        WHERE nama LIKE ? 
        ORDER BY nama ASC
    """, (param,))
    hasil = cursor.fetchall()
    conn.close()
    return hasil

def semua_produk():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, barcode, nama, harga, stok FROM produk")
    produk = cursor.fetchall()
    conn.close()
    return produk

# === Fungsi-fungsi Database Lainnya (Backup, User, dll) Tetap Sama ===

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
    return hashlib.sha256(password.encode()).hexdigest()

def tambah_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    try:
        cursor.execute("INSERT INTO user (username, password, role) VALUES (?, ?, ?)", (username, hashed_password))
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
    
    # Ambil role user jika password cocok
    cursor.execute("SELECT role FROM user WHERE username = ? AND password = ?", (username, hashed_password))
    data = cursor.fetchone()
    conn.close()

    if data:
        return data[0]
    else:
        return None

def buat_user_default():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM user")
    count = cursor.fetchone()[0]
    conn.close()
    
    if count == 0:
        tambah_user("admin", "admin")
        print("User default dibuat: username=admin, password=admin")

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
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE produk SET stok = ? WHERE id = ?", (stok_baru, id_produk))
    conn.commit()
    conn.close()

def backup_database_otomatis():
    if not DB_PATH.exists():
        return
    backup_folder = Path("data/backup")
    backup_folder.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_folder / f"pos_backup_{timestamp}.db"
    shutil.copy(DB_PATH, backup_path)
    return backup_path

def backup_database_harian():
    if not DB_PATH.exists():
        return
    backup_folder = Path("data/backup")
    backup_folder.mkdir(exist_ok=True)
    tanggal_hari_ini = datetime.now().strftime("%Y%m%d")
    backup_path = backup_folder / f"pos_backup_{tanggal_hari_ini}.db"
    if backup_path.exists():
        return
    shutil.copy(DB_PATH, backup_path)
    return backup_path

def cek_produk_stok_rendah(batas_stok=5):
    conn = create_connection()
    cursor = conn.cursor()
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
    from PyQt6.QtWidgets import QMessageBox
    produk_rendah = cek_produk_stok_rendah(batas_stok=5)
    if produk_rendah:
        pesan = "Produk dengan stok rendah:\n\n"
        for id_produk, barcode, nama, stok in produk_rendah:
            pesan += f"- {nama} (Barcode: {barcode}): {stok} pcs\n"
        pesan += f"\nTotal: {len(produk_rendah)} produk"
        msg = QMessageBox()
        msg.setWindowTitle("Peringatan Stok Rendah")
        msg.setText(pesan)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.exec()

def generate_barcode_gambar(barcode_value, nama_produk, output_path):
    barcode_folder = os.path.dirname(output_path)
    os.makedirs(barcode_folder, exist_ok=True)
    barcode = Code128(barcode_value, writer=ImageWriter())
    barcode_path = barcode.save(output_path)
    img = Image.open(barcode_path)
    new_height = img.height + 40
    new_img = Image.new('RGB', (img.width, new_height), 'white')
    new_img.paste(img, (0, 0))
    draw = ImageDraw.Draw(new_img)
    try:
        font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), nama_produk, font=font)
    text_width = bbox[2] - bbox[0]
    x = (img.width - text_width) // 2
    y = img.height + 10
    draw.text((x, y), nama_produk, fill='black', font=font)
    new_img.save(barcode_path)
    return barcode_path

def generate_semua_barcode_gambar():
    produk_list = semua_produk()
    if not produk_list:
        return []
    barcode_folder = "barcode"
    os.makedirs(barcode_folder, exist_ok=True)
    hasil = []
    for id_produk, barcode, nama, harga, stok in produk_list:
        if barcode:
            filename = f"{barcode}_{nama.replace(' ', '_')}.png"
            output_path = os.path.join(barcode_folder, filename)
            try:
                barcode_path = generate_barcode_gambar(barcode, nama, output_path)
                hasil.append(barcode_path)
            except Exception as e:
                print(f"Gagal generate barcode untuk {nama}: {str(e)}")
    return hasil

def semua_user():
    """Ambil semua user (ID, Username, Role) - Password tidak perlu diambil"""
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, username, role FROM user ORDER BY username ASC")
        hasil = cursor.fetchall()
        return hasil
    except Exception as e:
        print(f"Error ambil user: {e}")
        return[]
    finally:
        conn.close()

def tambah_user_baru(username, password, role="kasir"):
    """Tambah user baru ke database"""
    conn = create_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    try:
        cursor.execute("INSERT INTO user (username, password, role) VALUES (?,?, ?)", 
                       (username, hashed_password, role))
        conn.commit()
        return True
    except Exception as e:
        print(f"Gagal tambah user: {e}")
        return False
    finally:
        conn.close()

def update_user(id_user, username_baru, password_baru=None, role_baru="kasir"):
    """Update user (username, password, role) """
    conn = create_connection()
    cursor = conn.cursor()
    
    try:
        if password_baru:
            hashed_password = hash_password(password_baru)
            cursor.execute("UPDATE user SET username = ?, password = ? WHERE id = ?, role = ? WHERE id = ?",
                        (username_baru, hashed_password, role_baru, id_user))
        else:
            cursor.execute("UPDATE user SET username = ?, role = ? WHERE id = ?", 
                           (username_baru, role_baru, id_user))
        conn.commit()
        return True
    except Exception as e:
        print(f"Gagal update user: {e}")
    finally:
        conn.close()

def hapus_user(id_user):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user WHERE id = ?", (id_user,))
    conn.commit()
    conn.close()

def cek_username_sudah_ada(username, id_user_kecuali=None):
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
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO log_aktivitas (username, aktivitas, tanggal, detail)
        VALUES (?, ?, ?, ?)
    """, (username, aktivitas, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), detail))
    conn.commit()
    conn.close()

def ambil_log_aktivitas(username=None, limit=50):
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
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO produk (barcode, nama, harga, stok)
        VALUES (?, ?, ?, ?)
    """, (barcode, nama, harga, stok))
    conn.commit()
    conn.close()
    log_aktivitas_pengguna(username, "Tambah Produk", f"Barcode: {barcode}, Nama: {nama}")

def update_produk_dengan_log(id_produk, barcode, nama, harga, stok, username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE produk 
        SET barcode = ?, nama = ?, harga = ?, stok = ? 
        WHERE id = ?
    """, (barcode, nama, harga, stok, id_produk))
    conn.commit()
    conn.close()
    log_aktivitas_pengguna(username, "Edit Produk", f"ID: {id_produk}, Nama: {nama}")

def hapus_produk_dengan_log(id_produk, username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produk WHERE id = ?", (id_produk,))
    conn.commit()
    conn.close()
    log_aktivitas_pengguna(username, "Hapus Produk", f"ID: {id_produk}")
    
def get_info_dashboard():
    """Mengambil data untuk Dashboard: Omset Hari Ini, Total Transaksi, & Grafik 7 Hari"""
    conn = create_connection()
    cursor = conn.cursor()
    
    hari_ini = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute("""
        SELECT SUM(total), COUNT(id) 
        FROM transaksi 
        WHERE substr(tanggal, 1, 10) = ?
    """, (hari_ini,))
    
    row = cursor.fetchone()
    omset_hari_ini = row[0] if row[0] else 0
    transaksi_hari_ini = row[1] if row[1] else 0
    
    cursor.execute("""
        SELECT substr(tanggal, 1, 10) as tgl, SUM(total) 
        FROM transaksi 
        GROUP BY tgl 
        ORDER BY tgl DESC 
        LIMIT 7
    """)
    
    data_grafik = cursor.fetchall() 
    
    conn.close()
    
    data_grafik.reverse()
    
    return omset_hari_ini, transaksi_hari_ini, data_grafik