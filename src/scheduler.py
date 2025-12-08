"""
Scheduler untuk backup otomatis dan task terjadwal lainnya.
"""

import schedule
import time
from threading import Thread
from src.database import backup_database

def job_backup_malam():
    """Backup otomatis jam 23:00"""
    print("\n⏰ Menjalankan backup otomatis...")
    result = backup_database()
    if result:
        print(f"✅ Backup otomatis berhasil: {result}")
    else:
        print("❌ Backup otomatis gagal")

def run_scheduler():
    """
    Jalankan scheduler di background thread.
    Schedule: Backup setiap hari jam 23:00
    """
    # Jadwalkan backup jam 23:00
    schedule.every().day.at("23:00").do(job_backup_malam)
    
    print("📅 Scheduler aktif: Backup otomatis setiap hari jam 23:00")
    
    # Loop terus cek jadwal
    while True:
        schedule.run_pending()
        time.sleep(60)  # Cek setiap 1 menit

def start_scheduler():
    """Start scheduler di background thread"""
    scheduler_thread = Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()