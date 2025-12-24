"""
Kasir Window - REDESIGN SIDEBAR KANAN
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QLabel, 
    QPushButton, QDialog, QFrame
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
    """Kasir Window - Sidebar Layout"""
    
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
        self.setup_help_overlay(self.get_kasir_shortcuts())
        
        self.setWindowTitle("Mode Kasir - POS System")
        self.setGeometry(100, 100, 1200, 600)
    
    def setup_ui(self):
        """Setup UI - SIDEBAR LAYOUT"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # ========== LEFT SECTION (MAIN AREA) ==========
        left_section = QVBoxLayout()
        left_section.setSpacing(15)
        
        # TOP: Barcode input + Qty label
        top_layout = QHBoxLayout()
        
        lbl_barcode = QLabel("Scan:")
        lbl_barcode.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Scan barcode... (↓ = Table, 0-9 = Qty)")
        self.barcode_input.setMinimumHeight(45)
        self.barcode_input.returnPressed.connect(self.tambah_barang_ke_keranjang)
        
        self.lbl_qty_shortcut = QLabel("Qty: 1x")
        self.lbl_qty_shortcut.setFixedSize(100, 45)
        self.lbl_qty_shortcut.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_qty_shortcut.setStyleSheet("""
            QLabel {
                font-size: 16px; font-weight: bold; color: #4CAF50;
                background-color: #1E1E1E; border: 2px solid #4CAF50;
                border-radius: 5px;
            }
        """)
        
        top_layout.addWidget(lbl_barcode)
        top_layout.addWidget(self.barcode_input)
        top_layout.addWidget(self.lbl_qty_shortcut)
        left_section.addLayout(top_layout)
        
        # MIDDLE: Table
        self.table = SmartTable(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Nama", "Harga", "Qty", "Disc", "Subtotal"])
        self.table.setColumnHidden(0, True)
        self.table.stretch_column(1)
        self.table.set_column_width(2, 120)
        self.table.set_column_width(3, 50)
        self.table.set_column_width(4, 100)
        self.table.set_column_width(5, 130)
        
        left_section.addWidget(self.table)
        
        # BOTTOM: Action buttons (horizontal row)
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)
        
        style = StyleManager()
        
         # ✅ Semua button FIXED SIZE (120x40) - konsisten!
        self.btn_cari = QPushButton("🔍 Cari (F4)")
        self.btn_cari.setStyleSheet(style.get_button_style_fixed('primary', 130, 40))
        self.btn_cari.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cari.clicked.connect(self.buka_dialog_cari)
        
        self.btn_qty = QPushButton("✏️ Qty (F2)")
        self.btn_qty.setStyleSheet(style.get_button_style_fixed('warning', 120, 40))
        self.btn_qty.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_qty.clicked.connect(self.ubah_qty_item)
        
        self.btn_diskon = QPushButton("🎫 Disc (F8)")
        self.btn_diskon.setStyleSheet(style.get_button_style_fixed('info', 120, 40))
        self.btn_diskon.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_diskon.clicked.connect(self.ubah_diskon_item)
        
        self.btn_hapus = QPushButton("🗑️ Hapus (Del)")
        self.btn_hapus.setStyleSheet(style.get_button_style_fixed('danger', 140, 40))
        self.btn_hapus.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_hapus.clicked.connect(self.hapus_item_terpilih)
        
        self.btn_reset = QPushButton("🔄 Reset (F5)")
        self.btn_reset.setStyleSheet(style.get_button_style_fixed('default', 130, 40))
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self.reset_keranjang_confirm)
        
        bottom_layout.addWidget(self.btn_cari)
        bottom_layout.addWidget(self.btn_qty)
        bottom_layout.addWidget(self.btn_diskon)
        bottom_layout.addWidget(self.btn_hapus)
        bottom_layout.addWidget(self.btn_reset)
        bottom_layout.addStretch()
        
        left_section.addLayout(bottom_layout)
        
        main_layout.addLayout(left_section, 3)
        
        # ========== RIGHT SIDEBAR (ACTIONS) ==========
        right_sidebar = QVBoxLayout()
        right_sidebar.setSpacing(15)
        
        # CARD: Total
        card_total = QFrame()
        card_total.setStyleSheet("""
            QFrame {
                background-color: #1A1F2E;
                border: 2px solid #00F5FF;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        card_total_layout = QVBoxLayout(card_total)
        
        lbl_total_title = QLabel("TOTAL BELANJA")
        lbl_total_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_total_title.setStyleSheet("font-size: 14px; color: #aaa; border: none;")
        
        self.label_total = QLabel("Rp 0")
        self.label_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_total.setStyleSheet("""
            font-size: 32px; font-weight: bold; 
            color: #00F5FF; border: none;
        """)
        
        card_total_layout.addWidget(lbl_total_title)
        card_total_layout.addWidget(self.label_total)
        right_sidebar.addWidget(card_total)
        
        right_sidebar.addSpacing(10)
        
        # Button: Pending
        self.btn_pending = QPushButton("🔖 PENDING\n(F6)")
        self.btn_pending.setMinimumHeight(80)
        self.btn_pending.setStyleSheet("""
            QPushButton {
                background-color: #B026FF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #9C1FD9; }
            QPushButton:focus { border: 3px solid #fff; }
        """)
        self.btn_pending.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pending.clicked.connect(self.toggle_pending)
        right_sidebar.addWidget(self.btn_pending)
        
        right_sidebar.addSpacing(10)
        
        # Button: BAYAR (LARGE)
        self.btn_bayar = QPushButton("💰 BAYAR\n(F12)")
        self.btn_bayar.setMinimumHeight(120)
        self.btn_bayar.setStyleSheet("""
            QPushButton {
                background-color: #39FF14;
                color: #0A0A0F;
                border: none;
                border-radius: 10px;
                padding: 20px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2EE00F; }
            QPushButton:focus { border: 3px solid #fff; }
        """)
        self.btn_bayar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_bayar.clicked.connect(self.tampilkan_dialog_bayar)
        right_sidebar.addWidget(self.btn_bayar)
        
        right_sidebar.addStretch()
        
        main_layout.addLayout(right_sidebar, 1)
        
        self.update_pending_button()
    
    def setup_navigation(self):
        """Setup keyboard navigation"""
        
        # Barcode: 0-9 handled in eventFilter
        self.barcode_input.installEventFilter(self)
        
        # Bottom button row (circular)
        button_row = [
            self.btn_cari, self.btn_qty, self.btn_diskon,
            self.btn_hapus, self.btn_reset
        ]
        self.register_navigation_row(button_row, circular=True)
        
        for btn in button_row:
            self.register_navigation(btn, {
                Qt.Key.Key_Return: lambda b=btn: b.click(),
                Qt.Key.Key_Up: self.barcode_input,
                Qt.Key.Key_Down: lambda: self.focus_table_first_row(self.table)
            })
        
        # Table callbacks
        self.register_table_callbacks(self.table, {
            'edit': self.ubah_qty_item,
            'delete': self.hapus_item_terpilih,
            'focus_up': self.barcode_input,
            'focus_down': self.btn_pending
        })
        self.table.installEventFilter(self)
        
        # Sidebar buttons
        self.register_navigation(self.btn_pending, {
            Qt.Key.Key_Return: self.toggle_pending,
            Qt.Key.Key_Up: lambda: self.focus_table_last_row(self.table),
            Qt.Key.Key_Down: self.btn_bayar
        })
        
        self.register_navigation(self.btn_bayar, {
            Qt.Key.Key_Return: self.tampilkan_dialog_bayar,
            Qt.Key.Key_Up: self.btn_pending
        })
    
    def setup_global_shortcuts(self):
        """F-key shortcuts"""
        QShortcut(QKeySequence("F2"), self).activated.connect(self.ubah_qty_item)
        QShortcut(QKeySequence("F4"), self).activated.connect(self.buka_dialog_cari)
        QShortcut(QKeySequence("F5"), self).activated.connect(self.reset_keranjang_confirm)
        QShortcut(QKeySequence("F6"), self).activated.connect(self.toggle_pending)
        QShortcut(QKeySequence("F8"), self).activated.connect(self.ubah_diskon_item)
        QShortcut(QKeySequence("F12"), self).activated.connect(self.tampilkan_dialog_bayar)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self.hapus_item_terpilih)
    
    def eventFilter(self, obj, event):
        """Handle number keys for qty & navigation"""
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            
            if obj == self.barcode_input:
                # Number keys 0-9
                if Qt.Key.Key_0 <= key <= Qt.Key.Key_9 and not event.modifiers():
                    angka = key - Qt.Key.Key_0
                    self.qty_shortcut = 1 if angka == 0 else angka
                    self.update_qty_label()
                    return True
                
                # Down to table
                if key == Qt.Key.Key_Down:
                    if self.table.rowCount() > 0:
                        self.focus_table_first_row(self.table)
                    else:
                        self.btn_cari.setFocus()
                    return True
            
            elif obj == self.table:
                if key == Qt.Key.Key_Up and self.table.currentRow() == 0:
                    self.barcode_input.setFocus()
                    self.barcode_input.selectAll()
                    return True
        
        return super().eventFilter(obj, event)
    
    def keyPressEvent(self, event):
        """ESC with confirmation"""
        if event.key() == Qt.Key.Key_Escape:
            if self.keranjang_belanja or self.daftar_pending:
                pesan = "Yakin keluar?\n\n"
                if self.keranjang_belanja:
                    pesan += f"⚠️ Ada {len(self.keranjang_belanja)} item di keranjang\n"
                if self.daftar_pending:
                    pesan += f"⚠️ Ada {len(self.daftar_pending)} transaksi pending\n"
                
                if self.confirm_action("Keluar Kasir", pesan):
                    self.close()
            else:
                self.close()
            return
        
        super().keyPressEvent(event)
    
    # ========== QTY LABEL ==========
    
    def update_qty_label(self):
        """Update qty visual"""
        if self.qty_shortcut > 1:
            self.lbl_qty_shortcut.setText(f"Qty: {self.qty_shortcut}x")
            self.lbl_qty_shortcut.setStyleSheet("""
                QLabel {
                    font-size: 16px; font-weight: bold; color: #FF9800;
                    background-color: #1E1E1E; border: 2px solid #FF9800;
                    border-radius: 5px;
                }
            """)
        else:
            self.lbl_qty_shortcut.setText("Qty: 1x")
            self.lbl_qty_shortcut.setStyleSheet("""
                QLabel {
                    font-size: 16px; font-weight: bold; color: #4CAF50;
                    background-color: #1E1E1E; border: 2px solid #4CAF50;
                    border-radius: 5px;
                }
            """)
    
    # ========== CART OPERATIONS ==========
    
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
            
            # Check existing item
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
        """Update table & total"""
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
        
        self.label_total.setText(f"Rp {int(self.total_transaksi):,}")
    
    def reset_keranjang(self):
        """Clear cart"""
        self.keranjang_belanja = []
        self.total_transaksi = 0
        self.update_tabel_dan_total()
        self.barcode_input.setFocus()
    
    def reset_keranjang_confirm(self):
        """Reset with confirm"""
        if not self.keranjang_belanja:
            return
        if self.confirm_action("Batal Transaksi", "Kosongkan keranjang?"):
            self.reset_keranjang()
    
    # ========== ITEM ACTIONS ==========
    
    def ubah_qty_item(self):
        """Edit quantity"""
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
    
    # ========== DIALOGS ==========
    
    def buka_dialog_cari(self):
        """Open search dialog"""
        dialog = SearchDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.selected_barcode:
                self.barcode_input.setText(dialog.selected_barcode)
                self.tambah_barang_ke_keranjang()
        
        self.barcode_input.setFocus()
    
    def tampilkan_dialog_bayar(self):
        """Payment dialog"""
        if not self.keranjang_belanja:
            self.show_warning("Kosong", "Keranjang kosong.")
            self.barcode_input.setFocus()
            return
        
        dialog = MultiPaymentDialog(self.total_transaksi, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.payments:
            payments = dialog.payments
            kembalian = dialog.kembalian
            total_dibayar = sum(payments.values())
            
            self.simpan_transaksi(payments, total_dibayar, kembalian)
        
        self.barcode_input.setFocus()
    
    def toggle_pending(self):
        """Pending/Recall"""
        if self.keranjang_belanja:
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
        """Update pending button"""
        count = len(self.daftar_pending)
        
        if count == 0:
            self.btn_pending.setText("🔖 PENDING\n(F6)")
            self.btn_pending.setStyleSheet("""
                QPushButton {
                    background-color: #B026FF;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 15px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #9C1FD9; }
                QPushButton:focus { border: 3px solid #fff; }
            """)
        else:
            self.btn_pending.setText(f"🔖 PENDING ({count})\n(F6)")
            self.btn_pending.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 15px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #F57C00; }
                QPushButton:focus { border: 3px solid #fff; }
            """)
    
    # ========== SAVE TRANSACTION ==========
    
    def simpan_transaksi(self, payments_dict, total_dibayar, kembalian):
        """Save transaction dengan multi-payment"""
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
            
            # Save payment methods
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
            
            # Preview dengan payment breakdown
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
    
    # ========== KEYBOARD SHORTCUTS DEFINITION ==========      
    def get_kasir_shortcuts(self) -> dict:
        """Define keyboard shortcuts untuk kasir window"""
        return {
            "Scan Barang": [
                ("0-9", "Set quantity (tekan angka 1-9)"),
                ("Scan/Enter", "Tambah barang ke keranjang"),
                ("↓", "Pindah ke tabel belanja"),
            ],
            "Navigasi Tabel": [
                ("↑↓", "Navigate items di keranjang"),
                ("Ctrl+Up", "Kembali ke barcode input"),
                ("←→", "Navigate button row"),
            ],
            "Edit Item": [
                ("F2 / Enter", "Edit quantity item terpilih"),
                ("F8", "Edit diskon item terpilih"),
                ("Delete", "Hapus item dari keranjang"),
            ],
            "Actions": [
                ("F4", "Cari barang manual (tanpa barcode)"),
                ("F5", "Reset/Kosongkan keranjang"),
                ("F6", "Pending / Recall transaksi"),
                ("F12", "Proses pembayaran"),
            ],
            "Shortcuts Cepat": [
                ("Ctrl+F", "Focus ke pencarian (jika ada)"),
                ("ESC", "Keluar kasir (dengan konfirmasi)"),
            ],
        }