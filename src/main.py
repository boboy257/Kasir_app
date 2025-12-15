import sys
import signal
from PyQt6.QtWidgets import QApplication
from src.ui.windows.main_window import MainWindow
from src.ui.windows.login_window import LoginWindow
from src.database import create_tables, buat_user_default, backup_database_harian, tampilkan_notifikasi_stok_rendah
from src.ui.base.style_manager import StyleManager  # ← TAMBAH INI

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        # ✅ LOAD THEME GLOBAL (Sebelum window dibuat)
        style_manager = StyleManager()
        if not style_manager.load_theme("dark"):
            print("⚠️  Gagal load theme, pakai default Qt style")
        
        self.login_window = None
        self.main_window = None
    
    def show_login_first_time(self):
        """Hanya dipanggil saat aplikasi baru pertama kali buka"""
        self.login_window = LoginWindow(on_login_success=self.on_login_success)
        self.login_window.show()
    
    def on_login_success(self, username, role):
        """Saat login berhasil: Buka Main, lalu Tutup Login"""
        self.current_user = username 
        
        # 1. Buka Main Window DULUAN
        self.main_window = MainWindow(on_logout=self.on_logout)
        self.main_window.set_user_role(username, role)
        self.main_window.show()

        # Tampilkan notifikasi stok
        tampilkan_notifikasi_stok_rendah()

        # 2. Baru Tutup Login Window
        if self.login_window:
            self.login_window.close()
            self.login_window = None

    def on_logout(self):
        """Saat logout: Buka Login, lalu Tutup Main"""
        # 1. Buka Login Window DULUAN
        self.login_window = LoginWindow(on_login_success=self.on_login_success)
        self.login_window.show()

        # 2. Baru Tutup Main Window
        if self.main_window:
            self.main_window.close()
            self.main_window = None
    
    def run(self):
        # Izinkan Ctrl+C mematikan aplikasi seketika
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        
        # Setup Database
        create_tables()
        buat_user_default()
        from src.database import enable_wal_mode
        enable_wal_mode()
        backup_database_harian()
        
        # Backup Otomatis
        from src.scheduler import start_scheduler
        start_scheduler()
        
        # Tampilkan Login
        self.show_login_first_time()
        
        # Jalankan Aplikasi
        sys.exit(self.app.exec())

def main():
    controller = AppController()
    controller.run()

if __name__ == "__main__":
    main()