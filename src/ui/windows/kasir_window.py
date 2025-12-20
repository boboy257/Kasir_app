"""
Kasir Window - REFACTORED with SmartNavigation
===============================================
100% Keyboard-driven POS system - Optimized for speed
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QLabel, 
    QPushButton, QDialog
)
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QShortcut, QKeySequence
from datetime import datetime

from src.ui.base.base_window import BaseWindow
from src.ui.base.style_manager import StyleManager
from src.ui.widgets.smart_table import SmartTable
from src.ui.dialogs.multi_payment_dialog import MultiPaymentDialog
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
    Kasir Window - Full keyboard navigation optimized for speed
    
    Target: < 3 detik per item
    
    Layout Zones:
    - TOP: Barcode input + Button row (7 buttons)
    - MIDDLE: Shopping cart table
    - BOTTOM: Pending + Total + Bayar
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
        self.setup_global_shortcuts()
        
        self.setWindowTitle("Aplikasi Kasir - Mode Penjualan")
        self.setGeometry(100, 100, 1100, 600)
    
    def setup_ui(self):
        """Setup UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # ========== TOP ROW: Barcode + Buttons ==========
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
        
        style = StyleManager()
        
        # Button row (7 buttons)
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
        
        # ========== MIDDLE: TABLE ==========
        self.table = SmartTable(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Nama Produk", "Harga", "Qty", "Disc", "Subtotal"])
        self.table.setColumnHidden(0, True)
        self.table.stretch_column(1)
        self.table.set_column_width(2, 120)
        self.table.set_column_width(3, 50)
        self.table.set_column_width(4, 100)
        self.table.set_column_width(5, 120)
        
        layout.addWidget(self.table)
        
        # ========== BOTTOM: Actions ==========
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
    
    def setup_navigation(self):
        """
        ✨ SMART NAVIGATION SETUP
        
        Zones:
        1. Barcode input (PRIMARY - always return here!)
        2. Button row (5 buttons - circular)
        3. Table (middle zone)
        4. Bottom buttons (2 buttons)
        
        Critical: Focus ALWAYS returns to barcode after ANY action!
        """
        
        # ===== ZONE 1: BARCODE INPUT =====
        # Number keys 0-9 handled in keyPressEvent (special case)
        # Down = ke button row atau table
        self.barcode_input.installEventFilter(self)
        
        # ===== ZONE 2: BUTTON ROW (Circular!) =====
        button_row = [
            self.btn_cari,
            self.btn_qty,
            self.btn_diskon,
            self.btn_reset,
            self.btn_hapus
        ]
        
        self.register_navigation_row(button_row, circular=True)
        
        # All buttons: Enter = Click, Up = Barcode
        for btn in button_row:
            self.register_navigation(btn, {
                Qt.Key.Key_Return: lambda b=btn: b.click(),
                Qt.Key.Key_Up: self.barcode_input,
                Qt.Key.Key_Down: lambda: self.focus_table_first_row(self.table) if self.table.rowCount() > 0 else None
            })
        
        # ===== ZONE 3: TABLE =====
        self.register_table_callbacks(self.table, {
            'edit': self.ubah_qty_item,         # F2 / Enter
            'delete': self.hapus_item_terpilih, # Delete
            'focus_up': self.barcode_input,     # Up at row 0 → Barcode
            'focus_down': self.btn_pending      # Down at last → Pending
        })
        self.table.installEventFilter(self)
        
        # ===== ZONE 4: BOTTOM BUTTONS =====
        self.register_navigation_row([self.btn_pending, self.btn_bayar], circular=False)
        
        for btn in [self.btn_pending, self.btn_bayar]:
            self.register_navigation(btn, {
                Qt.Key.Key_Return: lambda b=btn: b.click(),
                Qt.Key.Key_Up: lambda: self.focus_table_last_row(self.table) if self.table.rowCount() > 0 else self.barcode_input.setFocus()
            })
    
    def setup_global_shortcuts(self):
        """Global F-key shortcuts (preserve existing functionality)"""
        QShortcut(QKeySequence("F2"), self).activated.connect(self.ubah_qty_item)
        QShortcut(QKeySequence("F4"), self).activated.connect(self.buka_dialog_cari)
        QShortcut(QKeySequence("F5"), self).activated.connect(self.reset_keranjang_confirm)
        QShortcut(QKeySequence("F6"), self).activated.connect(self.toggle_pending)
        QShortcut(QKeySequence("F8"), self).activated.connect(self.ubah_diskon_item)
        QShortcut(QKeySequence("F12"), self).activated.connect(self.tampilkan_dialog_bayar)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self.hapus_item_terpilih)
    
    def eventFilter(self, obj, event):
        """Handle special cases: Number keys 0-9 for qty, Barcode Down navigation"""
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            # ===== BARCODE INPUT: Number keys 0-9 =====
            if obj == self.barcode_input:
                
                # Number keys 0-9: Set qty shortcut
                if Qt.Key.Key_0 <= key <= Qt.Key.Key_9 and not event.modifiers():
                    angka = key - Qt.Key.Key_0
                    self.qty_shortcut = 1 if angka == 0 else angka
                    self.update_qty_label()
                    return True
                
                # Down: ke button row atau table
                if key == Qt.Key.Key_Down:
                    if self.table.rowCount() > 0:
                        self.focus_table_first_row(self.table)
                    else:
                        self.btn_cari.setFocus()
                    return True
            
            # ✅ TABLE UP MANUAL
            elif obj == self.table:
                if key == Qt.Key.Key_Up:
                    if self.table.currentRow() == 0:
                        self.barcode_input.setFocus()
                        self.barcode_input.selectAll()
                        return True
        
        return super().eventFilter(obj, event)
    
    def keyPressEvent(self, event):
        """Handle ESC with confirmation"""
        if event.key() == Qt.Key.Key_Escape:
            if self.keranjang_belanja or self.daftar_pending:
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
                self.close()
            return
        
        super().keyPressEvent(event)
    
    # ========== QTY LABEL UPDATE ==========
    
    def update_qty_label(self):
        """Update qty shortcut label visual"""
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
    
    # ========== CART OPERATIONS ==========
    
    def tambah_barang_ke_keranjang(self):
        """Add item to cart (PRIMARY FUNCTION - Speed critical!)"""
        barcode = self.barcode_input.text().strip()
        if not barcode:
            return
        
        produk = cari_produk_dari_barcode(barcode)
        
        if produk:
            id_produk, nama, harga, stok_db = produk
            
            # Validasi stok
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
            
            # Check if item already in cart
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
            
            # Add new item
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
            # Barcode not found - offer search
            reply = self.confirm_action("404", f"Barcode '{barcode}' tidak ada.\nCari manual?")
            if reply:
                self.buka_dialog_cari()
        
        # CRITICAL: Always return to barcode!
        self.barcode_input.clear()
        self.barcode_input.setFocus()
    
    def update_tabel_dan_total(self):
        """Update table and total display"""
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
    
    # ========== ITEM ACTIONS (Always return to barcode!) ==========
    
    def ubah_qty_item(self):
        """Edit quantity"""
        row = self.table.currentRow()
        if row < 0:
            self.show_warning("Pilih Item", "Pilih item di tabel dulu!")
            self.barcode_input.setFocus()
            return
        
        item = self.keranjang_belanja[row]
        
        # Get stok from database
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT stok FROM produk WHERE id = ?", (item['id'],))
        res = cursor.fetchone()
        conn.close()
        stok_db = res[0] if res else 0
        
        from PyQt6.QtWidgets import QInputDialog
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
        """Edit discount"""
        row = self.table.currentRow()
        if row < 0:
            self.show_warning("Pilih Item", "Pilih item di tabel dulu!")
            self.barcode_input.setFocus()
            return
        
        item = self.keranjang_belanja[row]
        
        from PyQt6.QtWidgets import QInputDialog
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
        """Delete item"""
        row = self.table.currentRow()
        if row >= 0:
            nama = self.keranjang_belanja[row]['nama']
            if self.confirm_action("Hapus", f"Hapus '{nama}'?"):
                del self.keranjang_belanja[row]
                self.update_tabel_dan_total()
        else:
            self.show_warning("Pilih Item", "Pilih item yang ingin dihapus.")
        
        self.barcode_input.setFocus()
    
    # ========== DIALOGS (Always return to barcode!) ==========
    
    def buka_dialog_cari(self):
        """Open search dialog"""
        dialog = SearchDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.selected_barcode:
                self.barcode_input.setText(dialog.selected_barcode)
                self.tambah_barang_ke_keranjang()
        
        self.barcode_input.setFocus()
    
    def tampilkan_dialog_bayar(self):
        """Payment dialog - MULTI PAYMENT VERSION"""
        if not self.keranjang_belanja:
            self.show_warning("Kosong", "Keranjang kosong.")
            self.barcode_input.setFocus()
            return
        
        # Multi-payment dialog
        dialog = MultiPaymentDialog(self.total_transaksi, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.payments:
            # Get payment details
            payments = dialog.payments  # {'cash': 50000, 'debit': 30000, ...}
            kembalian = dialog.kembalian
            total_dibayar = sum(payments.values())
            
            self.simpan_transaksi(payments, total_dibayar, kembalian)
        
        self.barcode_input.setFocus()
    
    def toggle_pending(self):
        """Pending/Recall"""
        if self.keranjang_belanja:
            # Save to pending
            if len(self.daftar_pending) >= self.MAX_PENDING:
                self.show_warning("Pending Penuh", 
                    f"Maksimal {self.MAX_PENDING} transaksi pending.")
                self.barcode_input.setFocus()
                return
            
            from PyQt6.QtWidgets import QInputDialog
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
            # Recall from pending
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
            
            elif result == 2:  # Delete
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
    
    # ========== SAVE TRANSACTION ==========
    
    def simpan_transaksi(self, payments_dict, total_dibayar, kembalian):
        """
        Save transaction dengan multi-payment
        
        Args:
            payments_dict: {'cash': 50000, 'debit': 30000, ...}
            total_dibayar: Total yang dibayarkan
            kembalian: Kembalian
        """
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
            
            # Insert detail items
            for item in self.keranjang_belanja:
                nilai_diskon = item.get('diskon', 0)
                cursor.execute("""
                    INSERT INTO detail_transaksi (transaksi_id, produk_nama, jumlah, harga, diskon, subtotal) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (transaksi_id, item['nama'], item['qty'], item['harga'], nilai_diskon, item['subtotal']))
                
                # Update stok
                cursor.execute("UPDATE produk SET stok = stok - ? WHERE id = ?", (item['qty'], item['id']))
            
            # ✅ NEW: Insert payment methods
            from src.database import simpan_payment_methods
            simpan_payment_methods(transaksi_id, payments_dict, cursor, conn)
            
            conn.commit()
            
            # Log aktivitas
            username = getattr(self, 'current_user', 'admin')
            log_aktivitas_pengguna(username, "Transaksi Penjualan", 
                f"ID: {transaksi_id}, Total: Rp {self.total_transaksi}")
            
            # Prepare struk data
            data_struk = [(item['nama'], int(item['harga']), item['qty'], int(item['subtotal'])) 
                        for item in self.keranjang_belanja]
            
            # Generate struk PDF
            filepath = None
            try:
                filepath = cetak_struk_pdf(
                    NAMA_TOKO, ALAMAT_TOKO, data_struk, 
                    int(self.total_transaksi), no_faktur,
                    total_dibayar, kembalian, username
                )
            except Exception as e:
                print(f"Error cetak struk: {e}")
            
            # ✅ NEW: Preview dengan payment breakdown
            tanggal_str = datetime.now().strftime('%d/%m/%Y %H:%M')
            preview_dialog = PreviewDialog(
                no_faktur, tanggal_str, username, data_struk,
                self.total_transaksi, total_dibayar, kembalian, self
            )
            
            if preview_dialog.exec() == QDialog.DialogCode.Accepted and preview_dialog.user_print:
                if filepath:
                    try:
                        import os, platform
                        if platform.system() == 'Windows':
                            os.startfile(filepath)
                    except Exception as e:
                        print(f"Gagal buka PDF: {e}")
                
                # Format payment summary
                payment_summary = "\n".join([
                    f"{method.upper()}: Rp {int(amount):,}" 
                    for method, amount in payments_dict.items()
                ])
                
                self.show_success("Berhasil", 
                    f"✅ Transaksi berhasil!\n\n"
                    f"Pembayaran:\n{payment_summary}\n\n"
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