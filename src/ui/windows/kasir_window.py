"""
Kasir Window - REFACTORED VERSION
==================================
Menggunakan BaseWindow dan extracted dialogs
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
    QAbstractItemView, QInputDialog, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QShortcut, QKeySequence
from datetime import datetime

from src.ui.base.base_window import BaseWindow
from src.ui.base.style_manager import StyleManager
from src.ui.dialogs.payment_dialog import PaymentDialog
from src.ui.dialogs.preview_dialog import PreviewDialog
from src.ui.dialogs.search_dialog import SearchDialog
from src.ui.dialogs.pending_dialog import PendingDialog

from src.database import (
    cari_produk_dari_barcode, create_connection, 
    generate_nomor_faktur, log_aktivitas_pengguna
)
from src.config import NAMA_TOKO, ALAMAT_TOKO
from src.cetak_struk import cetak_struk_pdf

class KasirWindow(BaseWindow):
    """
    Kasir window dengan fitur:
    - Scan barcode
    - Qty shortcut (angka 1-9)
    - Pending transaksi
    - Multi-item management
    """
    
    def __init__(self):
        super().__init__()
        
        self.qty_shortcut = 1
        self.keranjang_belanja = []
        self.daftar_pending = []
        self.total_transaksi = 0
        self.MAX_PENDING = 5
        
        self.setup_ui()
        self.setup_navigation()
        self.setup_shortcuts()
        
        # Window properties
        self.setWindowTitle("Aplikasi Kasir - Mode Penjualan")
        self.setGeometry(100, 100, 1100, 600)
    
    def setup_ui(self):
        """Setup UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # --- BAGIAN ATAS: Input & Controls ---
        top_layout = QHBoxLayout()
        
        lbl_barcode = QLabel("Scan Barcode:")
        lbl_barcode.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        # Qty Shortcut Label
        self.lbl_qty_shortcut = QLabel("Qty: 1x")
        self.lbl_qty_shortcut.setFixedWidth(80)
        self.lbl_qty_shortcut.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_qty_shortcut.setStyleSheet("""
            QLabel {
                font-size: 16px; font-weight: bold; color: #4CAF50;
                background-color: #1E1E1E; border: 2px solid #4CAF50;
                border-radius: 5px; padding: 5px;
            }
        """)
        
        # Barcode Input
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Scan barcode... (Panah Bawah ke Tabel)")
        self.barcode_input.setFixedHeight(40)
        self.barcode_input.returnPressed.connect(self.tambah_barang_ke_keranjang)
        self.barcode_input.installEventFilter(self)
        
        # Buttons
        style = StyleManager()
        
        self.btn_cari = QPushButton("Cari (F4)")
        self.btn_cari.setFixedHeight(40)
        self.btn_cari.setFixedWidth(80)
        self.btn_cari.clicked.connect(self.buka_dialog_cari)
        
        self.btn_qty = QPushButton("Qty (F2)")
        self.btn_qty.setFixedHeight(40)
        self.btn_qty.setFixedWidth(80)
        self.btn_qty.setStyleSheet(style.get_button_style('warning'))
        self.btn_qty.clicked.connect(self.ubah_qty_item)
        
        self.btn_diskon = QPushButton("Disc (F8)")
        self.btn_diskon.setFixedHeight(40)
        self.btn_diskon.setFixedWidth(80)
        self.btn_diskon.setStyleSheet("""
            QPushButton { background-color: #009688; color: white; border: none; }
            QPushButton:hover { background-color: #00796B; }
            QPushButton:focus { border: 2px solid #fff; }
        """)
        self.btn_diskon.clicked.connect(self.ubah_diskon_item)
        
        self.btn_reset = QPushButton("Reset (F5)")
        self.btn_reset.setFixedHeight(40)
        self.btn_reset.setFixedWidth(80)
        self.btn_reset.setStyleSheet("""
            QPushButton { background-color: #795548; color: white; border: none; }
            QPushButton:hover { background-color: #6D4C41; }
            QPushButton:focus { border: 2px solid #fff; }
        """)
        self.btn_reset.clicked.connect(self.reset_keranjang_confirm)
        
        self.btn_hapus = QPushButton("Hapus (Del)")
        self.btn_hapus.setFixedHeight(40)
        self.btn_hapus.setFixedWidth(90)
        self.btn_hapus.setStyleSheet(style.get_button_style('danger'))
        self.btn_hapus.clicked.connect(self.hapus_item_terpilih)
        
        top_layout.addWidget(lbl_barcode)
        top_layout.addWidget(self.barcode_input)
        top_layout.addWidget(self.lbl_qty_shortcut)
        top_layout.addWidget(self.btn_cari)
        top_layout.addWidget(self.btn_qty)
        top_layout.addWidget(self.btn_diskon)
        top_layout.addWidget(self.btn_reset)
        top_layout.addWidget(self.btn_hapus)
        layout.addLayout(top_layout)
        
        # --- TABEL KERANJANG ---
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Nama Produk", "Harga", "Qty", "Disc", "Subtotal"])
        self.table.setColumnHidden(0, True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.installEventFilter(self)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 50)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 120)
        
        layout.addWidget(self.table)
        
        # --- BAGIAN BAWAH: Total & Actions ---
        bottom_layout = QHBoxLayout()
        
        self.btn_pending = QPushButton("Pending (F6)")
        self.btn_pending.setFixedSize(120, 60)
        self.btn_pending.setStyleSheet("""
            QPushButton { background-color: #9C27B0; color: white; border: none; }
            QPushButton:hover { background-color: #7B1FA2; }
            QPushButton:focus { border: 2px solid #fff; }
        """)
        self.btn_pending.clicked.connect(self.toggle_pending)
        
        self.label_total = QLabel("Total: Rp 0")
        self.label_total.setStyleSheet("font-size: 24px; font-weight: bold; color: #2196F3;")
        
        self.btn_bayar = QPushButton("BAYAR (F12)")
        self.btn_bayar.setFixedSize(200, 60)
        self.btn_bayar.setStyleSheet(style.get_button_style('success') + "font-size: 18px;")
        self.btn_bayar.clicked.connect(self.tampilkan_dialog_bayar)
        
        bottom_layout.addWidget(self.btn_pending)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.label_total)
        bottom_layout.addWidget(self.btn_bayar)
        layout.addLayout(bottom_layout)
        
        # Update pending button
        self.update_pending_button()
    
    def setup_navigation(self):
        """Setup keyboard navigation"""
        # Barcode input: Down = ke tabel
        self.register_navigation(self.barcode_input, {
            Qt.Key.Key_Down: lambda: self.focus_table_last_row(self.table)
        })
        
        # Table: Up di baris 0 = balik ke input
        # (Handled in eventFilter karena conditional)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        QShortcut(QKeySequence("F2"), self).activated.connect(self.ubah_qty_item)
        QShortcut(QKeySequence("F4"), self).activated.connect(self.buka_dialog_cari)
        QShortcut(QKeySequence("F5"), self).activated.connect(self.reset_keranjang_confirm)
        QShortcut(QKeySequence("F6"), self).activated.connect(self.toggle_pending)
        QShortcut(QKeySequence("F8"), self).activated.connect(self.ubah_diskon_item)
        QShortcut(QKeySequence("F12"), self).activated.connect(self.tampilkan_dialog_bayar)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self.hapus_item_terpilih)
    
    def eventFilter(self, obj, event):
        """Handle keyboard events"""
        if event.type() == QEvent.Type.KeyPress:
            
            # Qty shortcut (angka 0-9)
            if obj == self.barcode_input and not event.modifiers():
                key = event.key()
                if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
                    angka = key - Qt.Key.Key_0
                    self.qty_shortcut = 1 if angka == 0 else angka
                    self.update_qty_label()
                    return True
            
            # Table: Up di baris 0 = balik ke input
            if obj == self.table and event.key() == Qt.Key.Key_Up:
                if self.table.currentRow() == 0:
                    self.barcode_input.setFocus()
                    return True
        
        return super().eventFilter(obj, event)
    
    def handle_escape(self):
        """Override ESC: Konfirmasi jika ada transaksi"""
        if self.keranjang_belanja:
            if self.confirm_action("Keluar", "Transaksi belum selesai. Yakin ingin keluar?"):
                self.close()
                return True
            return False
        else:
            self.close()
            return True
    
    # ========== QTY SHORTCUT ==========
    
    def update_qty_label(self):
        """Update tampilan qty shortcut label"""
        if self.qty_shortcut > 1:
            self.lbl_qty_shortcut.setText(f"Qty: {self.qty_shortcut}x")
            self.lbl_qty_shortcut.setStyleSheet("""
                QLabel {
                    font-size: 16px; font-weight: bold; color: #FF9800;
                    background-color: #1E1E1E; border: 2px solid #FF9800;
                    border-radius: 5px; padding: 5px;
                }
            """)
        else:
            self.lbl_qty_shortcut.setText("Qty: 1x")
            self.lbl_qty_shortcut.setStyleSheet("""
                QLabel {
                    font-size: 16px; font-weight: bold; color: #4CAF50;
                    background-color: #1E1E1E; border: 2px solid #4CAF50;
                    border-radius: 5px; padding: 5px;
                }
            """)
    
    # ========== KERANJANG MANAGEMENT ==========
    
    def tambah_barang_ke_keranjang(self):
        """Add item to cart"""
        barcode = self.barcode_input.text().strip()
        if not barcode:
            return
        
        produk = cari_produk_dari_barcode(barcode)
        
        if produk:
            id_produk, nama, harga, stok_db = produk
            
            # Cek stok
            if stok_db <= 0:
                self.show_warning("Stok Habis", f"Stok '{nama}' kosong!")
                self.barcode_input.clear()
                return
            
            if self.qty_shortcut > stok_db:
                self.show_warning("Stok Kurang", 
                    f"Stok hanya {stok_db}, tidak cukup untuk {self.qty_shortcut} pcs!")
                self.barcode_input.clear()
                self.qty_shortcut = 1
                self.update_qty_label()
                return
            
            # Cek apakah item sudah ada di keranjang
            item_found = False
            for item in self.keranjang_belanja:
                if item['id'] == id_produk:
                    if item['qty'] + self.qty_shortcut > stok_db:
                        self.show_warning("Stok Habis", f"Sisa stok hanya {stok_db}.")
                        self.barcode_input.clear()
                        self.qty_shortcut = 1
                        self.update_qty_label()
                        return
                    
                    item['qty'] += self.qty_shortcut
                    item_found = True
                    break
            
            # Tambah item baru
            if not item_found:
                self.keranjang_belanja.append({
                    'id': id_produk,
                    'nama': nama,
                    'harga': harga,
                    'qty': self.qty_shortcut,
                    'diskon': 0,
                    'subtotal': harga * self.qty_shortcut
                })
            
            self.update_tabel_dan_total()
            self.qty_shortcut = 1
            self.update_qty_label()
        else:
            # Barang tidak ditemukan
            reply = self.confirm_action("404", f"Barcode '{barcode}' tidak ada.\nCari manual?")
            if reply:
                self.buka_dialog_cari()
        
        self.barcode_input.clear()
        self.barcode_input.setFocus()
    
    def update_tabel_dan_total(self):
        """Update table dan total"""
        self.table.setRowCount(0)
        self.total_transaksi = 0
        
        for row, item in enumerate(self.keranjang_belanja):
            self.table.insertRow(row)
            
            harga_bersih = item['harga'] - item['diskon']
            item['subtotal'] = item['qty'] * harga_bersih
            
            self.table.setItem(row, 0, QTableWidgetItem(str(item['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(item['nama']))
            self.table.setItem(row, 2, QTableWidgetItem(f"Rp {int(item['harga']):,}"))
            self.table.setItem(row, 3, QTableWidgetItem(str(item['qty'])))
            self.table.setItem(row, 4, QTableWidgetItem(f"Rp {int(item['diskon']):,}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"Rp {int(item['subtotal']):,}"))
            
            self.total_transaksi += item['subtotal']
        
        self.label_total.setText(f"Total: Rp {int(self.total_transaksi):,}")
    
    def reset_keranjang(self):
        """Clear cart"""
        self.keranjang_belanja = []
        self.total_transaksi = 0
        self.update_tabel_dan_total()
        self.barcode_input.setFocus()
    
    def reset_keranjang_confirm(self):
        """Reset dengan konfirmasi"""
        if not self.keranjang_belanja:
            return
        if self.confirm_action("Batal Transaksi", "Kosongkan keranjang?"):
            self.reset_keranjang()
    
    # ========== ITEM ACTIONS ==========
    
    def ubah_qty_item(self):
        """Ubah jumlah item"""
        row = self.table.currentRow()
        if row < 0:
            self.show_warning("Pilih Item", "Pilih item di tabel dulu!")
            return
        
        item = self.keranjang_belanja[row]
        
        # Cek stok database
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT stok FROM produk WHERE id = ?", (item['id'],))
        res = cursor.fetchone()
        conn.close()
        stok_db = res[0] if res else 0
        
        qty_baru, ok = QInputDialog.getInt(
            self, "Ubah Jumlah", 
            f"Stok: {stok_db}\nJumlah baru:", 
            value=item['qty'], min=1, max=10000
        )
        
        if ok:
            if qty_baru > stok_db:
                self.show_error("Stok Kurang", f"Stok hanya ada {stok_db}!")
            else:
                self.keranjang_belanja[row]['qty'] = qty_baru
                self.update_tabel_dan_total()
                self.barcode_input.setFocus()
    
    def ubah_diskon_item(self):
        """Ubah diskon item"""
        row = self.table.currentRow()
        if row < 0:
            self.show_warning("Pilih Item", "Pilih item di tabel dulu!")
            return
        
        item = self.keranjang_belanja[row]
        
        diskon_baru, ok = QInputDialog.getInt(
            self, "Diskon Manual", 
            f"Potongan (Rp) untuk '{item['nama']}':",
            value=item['diskon'], min=0, max=int(item['harga'])
        )
        
        if ok:
            self.keranjang_belanja[row]['diskon'] = diskon_baru
            self.update_tabel_dan_total()
            self.barcode_input.setFocus()
    
    def hapus_item_terpilih(self):
        """Hapus item dari keranjang"""
        row = self.table.currentRow()
        if row >= 0:
            nama = self.keranjang_belanja[row]['nama']
            if self.confirm_action("Hapus", f"Hapus '{nama}'?"):
                del self.keranjang_belanja[row]
                self.update_tabel_dan_total()
                self.barcode_input.setFocus()
        else:
            self.show_warning("Pilih Item", "Pilih item yang ingin dihapus.")
    
    # ========== DIALOGS ==========
    
    def buka_dialog_cari(self):
        """Buka dialog cari barang"""
        dialog = SearchDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.selected_barcode:
                self.barcode_input.setText(dialog.selected_barcode)
                self.tambah_barang_ke_keranjang()
    
    def tampilkan_dialog_bayar(self):
        """Tampilkan dialog pembayaran"""
        if not self.keranjang_belanja:
            self.show_warning("Kosong", "Keranjang kosong.")
            return
        
        dialog = PaymentDialog(self.total_transaksi, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.pembayaran_sukses:
            self.simpan_transaksi(dialog.uang_diterima, dialog.kembalian)
    
    # ========== PENDING MANAGEMENT ==========
    
    def toggle_pending(self):
        """Toggle antara Pending (simpan) dan Recall (ambil)"""
        # CASE 1: Ada keranjang -> PENDING
        if self.keranjang_belanja:
            if len(self.daftar_pending) >= self.MAX_PENDING:
                self.show_warning("Pending Penuh", 
                    f"Maksimal {self.MAX_PENDING} transaksi pending.\n"
                    "Selesaikan transaksi pending lama terlebih dahulu.")
                self.barcode_input.setFocus()
                return
            
            note, ok = QInputDialog.getText(
                self, "Catatan Pending", 
                "Catatan (opsional, misal: 'Ibu baju merah'):"
            )
            
            if not ok:
                self.barcode_input.setFocus()
                return
            
            # Simpan pending
            pending_data = {
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'note': note.strip(),
                'total': self.total_transaksi,
                'keranjang': list(self.keranjang_belanja)
            }
            
            self.daftar_pending.append(pending_data)
            self.keranjang_belanja = []
            self.update_tabel_dan_total()
            self.update_pending_button()
            
            self.show_success("Pending Tersimpan", 
                f"Transaksi disimpan!\n\n"
                f"Total Pending: {len(self.daftar_pending)}\n"
                f"Note: {note if note else '-'}")
            
            self.barcode_input.setFocus()
        
        # CASE 2: Ada pending -> RECALL
        elif self.daftar_pending:
            dialog = PendingDialog(self.daftar_pending, self)
            result = dialog.exec()
            
            if result == QDialog.DialogCode.Accepted:  # Recall
                idx = dialog.selected_index
                if idx is not None:
                    pending = self.daftar_pending[idx]
                    self.keranjang_belanja = list(pending['keranjang'])
                    self.update_tabel_dan_total()
                    self.daftar_pending.pop(idx)
                    self.update_pending_button()
                    
                    self.show_success("Recall Berhasil", 
                        f"Transaksi di-recall!\n\n"
                        f"Note: {pending.get('note', '-')}\n"
                        f"Total: Rp {int(pending['total']):,}")
            
            elif result == 2:  # Hapus
                idx = dialog.selected_index
                if idx is not None:
                    self.daftar_pending.pop(idx)
                    self.update_pending_button()
                    self.show_success("Dihapus", "Transaksi pending dihapus")
            
            self.barcode_input.setFocus()
        
        # CASE 3: Tidak ada apa-apa
        else:
            self.show_warning("Info", "Tidak ada transaksi untuk di-pending atau di-recall")
            self.barcode_input.setFocus()
    
    def update_pending_button(self):
        """Update tampilan tombol pending"""
        count = len(self.daftar_pending)
        
        if count == 0:
            self.btn_pending.setText("Pending (F6)")
            self.btn_pending.setStyleSheet("""
                QPushButton { background-color: #9C27B0; color: white; border: none; }
                QPushButton:hover { background-color: #7B1FA2; }
                QPushButton:focus { border: 2px solid #fff; }
            """)
        else:
            self.btn_pending.setText(f"Pending ({count}) F6")
            self.btn_pending.setStyleSheet("""
                QPushButton { background-color: #FF9800; color: white; border: none; }
                QPushButton:hover { background-color: #F57C00; }
                QPushButton:focus { border: 2px solid #fff; }
            """)
    
    # ========== TRANSAKSI ==========
    
    def simpan_transaksi(self, uang_diterima, kembalian):
        """Simpan transaksi ke database"""
        conn = create_connection()
        cursor = conn.cursor()
        
        try:
            no_faktur = generate_nomor_faktur()
            tanggal_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Insert transaksi
            cursor.execute(
                "INSERT INTO transaksi (no_faktur, tanggal, total) VALUES (?, ?, ?)",
                (no_faktur, tanggal_sekarang, self.total_transaksi)
            )
            transaksi_id = cursor.lastrowid
            
            # Insert detail & update stok
            for item in self.keranjang_belanja:
                nilai_diskon = item.get('diskon', 0)
                cursor.execute("""
                    INSERT INTO detail_transaksi (transaksi_id, produk_nama, jumlah, harga, diskon, subtotal) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (transaksi_id, item['nama'], item['qty'], item['harga'], nilai_diskon, item['subtotal']))
                
                cursor.execute("UPDATE produk SET stok = stok - ? WHERE id = ?", (item['qty'], item['id']))
            
            conn.commit()
            
            # Log aktivitas
            username = getattr(self, 'current_user', 'admin')
            log_aktivitas_pengguna(username, "Transaksi Penjualan", 
                f"ID: {transaksi_id}, Total: Rp {self.total_transaksi}")
            
            # Cetak struk
            data_struk = [(item['nama'], int(item['harga']), item['qty'], int(item['subtotal'])) 
                          for item in self.keranjang_belanja]
            
            filepath = None
            try:
                filepath = cetak_struk_pdf(
                    NAMA_TOKO, ALAMAT_TOKO, data_struk, 
                    int(self.total_transaksi), no_faktur,
                    uang_diterima, kembalian, username
                )
            except Exception as e:
                print(f"Error cetak struk: {e}")
            
            # Preview dialog
            tanggal_str = datetime.now().strftime('%d/%m/%Y %H:%M')
            preview_dialog = PreviewDialog(
                no_faktur, tanggal_str, username, data_struk,
                self.total_transaksi, uang_diterima, kembalian, self
            )
            
            if preview_dialog.exec() == QDialog.DialogCode.Accepted and preview_dialog.user_print:
                if filepath:
                    try:
                        import os, platform
                        if platform.system() == 'Windows':
                            os.startfile(filepath)
                    except Exception as e:
                        print(f"Gagal buka PDF: {e}")
                
                self.show_success("Berhasil", 
                    f"✅ Transaksi berhasil!\n\n"
                    f"Bayar: Rp {int(uang_diterima):,}\n"
                    f"Kembali: Rp {int(kembalian):,}")
            else:
                self.show_success("Transaksi Berhasil", 
                    f"✅ Transaksi tersimpan\n\n"
                    f"No. Faktur: {no_faktur}\n"
                    f"Total: Rp {int(self.total_transaksi):,}\n\n"
                    f"Struk tersimpan di folder 'struk'")
            
            self.reset_keranjang()
            
        except Exception as e:
            conn.rollback()
            self.show_error("Error", f"Gagal simpan: {str(e)}")
        finally:
            conn.close()