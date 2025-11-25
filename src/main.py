import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.ui.login_window import LoginWindow
from src.database import create_tables, buat_user_default, backup_database_harian, tampilkan_notifikasi_stok_rendah

class AppController:
    """Kelas untuk mengatur alur aplikasi: login -> main window"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_window = None
        self.main_window = None
    
    def show_login(self):
        """Tampilkan jendela login"""
        self.login_window = LoginWindow(on_login_success=self.on_login_success)
        self.login_window.show()
    
    def on_login_success(self):
        """Fungsi dipanggil saat login sukses"""
        # Sembunyikan jendela login
        if self.login_window:
            self.login_window.hide()
        
        # Tampilkan notifikasi stok rendah
        tampilkan_notifikasi_stok_rendah()
        
        # Tampilkan jendela utama
        self.main_window = MainWindow()
        self.main_window.show()
    
    def run(self):
        """Jalankan aplikasi"""
        create_tables()
        buat_user_default()
        backup_database_harian()
        self.show_login()
        sys.exit(self.app.exec())

def main():
    controller = AppController()
    controller.run()

if __name__ == "__main__":
    main()