from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QLabel, 
    QPushButton, QInputDialog, QDialog
)
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QShortcut, QKeySequence
from datetime import datetime

from src.ui.base.base_window import BaseWindow
from src.ui.base.style_manager import StyleManager
from src.ui.widgets.smart_table import SmartTable
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
    Kasir Window - 100% Keyboard Navigation
    
    Navigation Map:
    - Barcode Input: Always return here after actions
    - Number 0-9: Set qty shortcut
    - F4: Search dialog
    - F2: Edit qty (table selected)
    - F8: Edit discount (table selected)
    - Delete: Hapus item (table selected)
    - F5: Reset cart
    - F6: Pending/Recall
    - F12: Payment
    - Down: Ke table
    - Up (at table row 0): Balik ke barcode
    """
    
    def __init__(self):
        super().__init__()
        
        self.qty_shortcut = 1
        self.keranjang_belanja = []
        self.daftar_pending = []
        self.total_transaksi = 0
        self.MAX_PENDING = 5
        
        self.setup_ui()
        self.setup_shortcuts()
        
        self.setWindowTitle("Aplikasi Kasir - Mode Penjualan")
        self.setGeometry(100, 100, 1100, 600)
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # TOP: Input & Controls
        top_layout = QHBoxLayout()
        
        lbl_barcode = QLabel("Scan Barcode:")
        lbl_barcode.setStyleSheet("font-size: 14px; font-weight: bold;")
        
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
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Scan barcode... (↓ = Table, 0-9 = Qty)")
        self.barcode_input.setFixedHeight(40)
        self.barcode_input.returnPressed.connect(self.tambah_barang_ke_keranjang)
        self.barcode_input.installEventFilter(self)
        
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
        
        # TABLE
        self.table = SmartTable(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Nama Produk", "Harga", "Qty", "Disc", "Subtotal"])
        self.table.setColumnHidden(0, True)
        self.table.stretch_column(1)
        self.table.set_column_width(2, 120)
        self.table.set_column_width(3, 50)
        self.table.set_column_width(4, 100)
        self.table.set_column_width(5, 120)
        self.table.installEventFilter(self)
        
        layout.addWidget(self.table)
        
        # BOTTOM
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
        
        self.update_pending_button()
        
      
    def keyPressEvent(self, event):
        """Handle ESC key untuk keluar kasir"""
        if event.key() == Qt.Key.Key_Escape:
            # Cek apakah ada transaksi aktif ATAU ada pending
            if self.keranjang_belanja or self.daftar_pending:
                # Buat pesan yang informatif
                pesan = "Yakin ingin keluar?\n\n"
                
                if self.keranjang_belanja:
                    pesan += f"⚠️ Ada {len(self.keranjang_belanja)} barang di keranjang\n"
                    pesan += "   (Tekan F6 untuk Pending)\n\n"
                
                if self.daftar_pending:
                    pesan += f"⚠️ Ada {len(self.daftar_pending)} transaksi pending\n"
                    pesan += "   (Data pending akan hilang!)\n\n"
                
                if self.confirm_action("Keluar Kasir", pesan):
                    self.close()
            else:
                # Keranjang kosong DAN tidak ada pending
                self.close()
            return
        
        super().keyPressEvent(event)
             
    def setup_shortcuts(self):
        """Global F-key shortcuts"""
        QShortcut(QKeySequence("F2"), self).activated.connect(self.ubah_qty_item)
        QShortcut(QKeySequence("F4"), self).activated.connect(self.buka_dialog_cari)
        QShortcut(QKeySequence("F5"), self).activated.connect(self.reset_keranjang_confirm)
        QShortcut(QKeySequence("F6"), self).activated.connect(self.toggle_pending)
        QShortcut(QKeySequence("F8"), self).activated.connect(self.ubah_diskon_item)
        QShortcut(QKeySequence("F12"), self).activated.connect(self.tampilkan_dialog_bayar)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self.hapus_item_terpilih)
    
    def eventFilter(self, obj, event):
        """Handle all keyboard navigation"""
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            
            # ===== BARCODE INPUT =====
            if obj == self.barcode_input:
                # Number keys 0-9: Set qty shortcut
                if Qt.Key.Key_0 <= key <= Qt.Key.Key_9 and not event.modifiers():
                    angka = key - Qt.Key.Key_0
                    self.qty_shortcut = 1 if angka == 0 else angka
                    self.update_qty_label()
                    return True
                
                # Down arrow: Jump to table
                if key == Qt.Key.Key_Down:
                    if self.table.rowCount() > 0:
                        self.table.setFocus()
                        self.table.selectRow(0)
                    return True
            
            # ===== TABLE =====
            elif obj == self.table:
                # Up at row 0: Back to barcode input
                if key == Qt.Key.Key_Up:
                    if self.table.currentRow() == 0:
                        self.barcode_input.setFocus()
                        self.barcode_input.selectAll()
                        return True
                
                # F2 or Enter: Edit qty
                if key in (Qt.Key.Key_F2, Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self.ubah_qty_item()
                    return True
                
                # Delete: Remove item
                if key == Qt.Key.Key_Delete:
                    self.hapus_item_terpilih()
                    return True
                
                # F8: Edit discount
                if key == Qt.Key.Key_F8:
                    self.ubah_diskon_item()
                    return True
        
        return super().eventFilter(obj, event)
    
    def handle_escape(self):
        """ESC: Confirm exit if cart not empty"""
        if self.keranjang_belanja:
            if self.confirm_action("Keluar", "Transaksi belum selesai. Yakin keluar?"):
                self.close()
                return True
            return False
        else:
            self.close()
            return True
    
    def update_qty_label(self):
        """Update qty shortcut label"""
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
    
    def tambah_barang_ke_keranjang(self):
        """Add item to cart"""
        barcode = self.barcode_input.text().strip()
        if not barcode:
            return
        
        produk = cari_produk_dari_barcode(barcode)
        
        if produk:
            id_produk, nama, harga, stok_db = produk
            
            if stok_db <= 0:
                self.show_warning("Stok Habis", f"Stok '{nama}' kosong!")
                self.barcode_input.clear()
                self.barcode_input.setFocus()
                return
            
            if self.qty_shortcut > stok_db:
                self.show_warning("Stok Kurang", 
                    f"Stok hanya {stok_db}, tidak cukup untuk {self.qty_shortcut} pcs!")
                self.barcode_input.clear()
                self.qty_shortcut = 1
                self.update_qty_label()
                self.barcode_input.setFocus()
                return
            
            item_found = False
            for item in self.keranjang_belanja:
                if item['id'] == id_produk:
                    if item['qty'] + self.qty_shortcut > stok_db:
                        self.show_warning("Stok Habis", f"Sisa stok hanya {stok_db}.")
                        self.barcode_input.clear()
                        self.qty_shortcut = 1
                        self.update_qty_label()
                        self.barcode_input.setFocus()
                        return
                    
                    item['qty'] += self.qty_shortcut
                    item_found = True
                    break
            
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
            reply = self.confirm_action("404", f"Barcode '{barcode}' tidak ada.\nCari manual?")
            if reply:
                self.buka_dialog_cari()
        
        self.barcode_input.clear()
        self.barcode_input.setFocus()
    
    def update_tabel_dan_total(self):
        """Update table and total"""
        self.table.clear_table()
        self.total_transaksi = 0
        
        from PyQt6.QtWidgets import QTableWidgetItem
        
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
        """Reset cart with confirmation"""
        if not self.keranjang_belanja:
            return
        if self.confirm_action("Batal Transaksi", "Kosongkan keranjang?"):
            self.reset_keranjang()
    
    def ubah_qty_item(self):
        """Edit quantity - Always return to barcode input after"""
        row = self.table.currentRow()
        if row < 0:
            self.show_warning("Pilih Item", "Pilih item di tabel dulu!")
            self.barcode_input.setFocus()
            return
        
        item = self.keranjang_belanja[row]
        
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
        """Edit discount - Always return to barcode input after"""
        row = self.table.currentRow()
        if row < 0:
            self.show_warning("Pilih Item", "Pilih item di tabel dulu!")
            self.barcode_input.setFocus()
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
        """Delete item - Always return to barcode input after"""
        row = self.table.currentRow()
        if row >= 0:
            nama = self.keranjang_belanja[row]['nama']
            if self.confirm_action("Hapus", f"Hapus '{nama}'?"):
                del self.keranjang_belanja[row]
                self.update_tabel_dan_total()
        else:
            self.show_warning("Pilih Item", "Pilih item yang ingin dihapus.")
        
        self.barcode_input.setFocus()
    
    def buka_dialog_cari(self):
        """Open search dialog - Return to barcode after"""
        dialog = SearchDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.selected_barcode:
                self.barcode_input.setText(dialog.selected_barcode)
                self.tambah_barang_ke_keranjang()
        
        self.barcode_input.setFocus()
    
    def tampilkan_dialog_bayar(self):
        """Payment dialog - Return to barcode after"""
        if not self.keranjang_belanja:
            self.show_warning("Kosong", "Keranjang kosong.")
            self.barcode_input.setFocus()
            return
        
        dialog = PaymentDialog(self.total_transaksi, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.pembayaran_sukses:
            self.simpan_transaksi(dialog.uang_diterima, dialog.kembalian)
        
        self.barcode_input.setFocus()
    
    def toggle_pending(self):
        """Pending/Recall - Return to barcode after"""
        if self.keranjang_belanja:
            if len(self.daftar_pending) >= self.MAX_PENDING:
                self.show_warning("Pending Penuh", 
                    f"Maksimal {self.MAX_PENDING} transaksi pending.")
                self.barcode_input.setFocus()
                return
            
            note, ok = QInputDialog.getText(
                self, "Catatan Pending", 
                "Catatan (opsional):"
            )
            
            if ok:
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
                    f"Total Pending: {len(self.daftar_pending)}")
        
        elif self.daftar_pending:
            dialog = PendingDialog(self.daftar_pending, self)
            result = dialog.exec()
            
            if result == QDialog.DialogCode.Accepted:
                idx = dialog.selected_index
                if idx is not None:
                    pending = self.daftar_pending[idx]
                    self.keranjang_belanja = list(pending['keranjang'])
                    self.update_tabel_dan_total()
                    self.daftar_pending.pop(idx)
                    self.update_pending_button()
            
            elif result == 2:
                idx = dialog.selected_index
                if idx is not None:
                    self.daftar_pending.pop(idx)
                    self.update_pending_button()
        
        else:
            self.show_warning("Info", "Tidak ada transaksi pending.")
        
        self.barcode_input.setFocus()
    
    def update_pending_button(self):
        """Update pending button appearance"""
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
    
    def simpan_transaksi(self, uang_diterima, kembalian):
        """Save transaction"""
        conn = create_connection()
        cursor = conn.cursor()
        
        try:
            no_faktur = generate_nomor_faktur()
            tanggal_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute(
                "INSERT INTO transaksi (no_faktur, tanggal, total) VALUES (?, ?, ?)",
                (no_faktur, tanggal_sekarang, self.total_transaksi)
            )
            transaksi_id = cursor.lastrowid
            
            for item in self.keranjang_belanja:
                nilai_diskon = item.get('diskon', 0)
                cursor.execute("""
                    INSERT INTO detail_transaksi (transaksi_id, produk_nama, jumlah, harga, diskon, subtotal) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (transaksi_id, item['nama'], item['qty'], item['harga'], nilai_diskon, item['subtotal']))
                
                cursor.execute("UPDATE produk SET stok = stok - ? WHERE id = ?", (item['qty'], item['id']))
            
            conn.commit()
            
            username = getattr(self, 'current_user', 'admin')
            log_aktivitas_pengguna(username, "Transaksi Penjualan", 
                f"ID: {transaksi_id}, Total: Rp {self.total_transaksi}")
            
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
                    f"Total: Rp {int(self.total_transaksi):,}")
            
            self.reset_keranjang()
            
        except Exception as e:
            conn.rollback()
            self.show_error("Error", f"Gagal simpan: {str(e)}")
        finally:
            conn.close()