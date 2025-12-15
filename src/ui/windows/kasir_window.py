from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QHBoxLayout,
    QLineEdit, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QDialog, QFormLayout, QHeaderView, QAbstractItemView,
    QInputDialog, QTextEdit, QListWidget
)
# [PENTING] Pastikan import ini ada
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import Qt, QEvent
from src.database import cari_produk_dari_barcode, create_connection, cari_produk_by_nama_partial, semua_produk
from src.config import NAMA_TOKO, ALAMAT_TOKO
from src.cetak_struk import cetak_struk_pdf
from datetime import datetime

# --- CLASS DIALOG PREVIEW STRUK ---
class DialogPreviewStruk(QDialog):
    def __init__(self, no_faktur, tanggal, kasir, keranjang, total, uang_diterima, kembalian, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preview Struk Transaksi")
        self.setFixedSize(500, 600)
        
        self.no_faktur = no_faktur
        self.tanggal = tanggal
        self.kasir = kasir
        self.keranjang = keranjang
        self.total = total
        self.uang_diterima = uang_diterima
        self.kembalian = kembalian
        self.user_print = False  # Flag apakah user mau print
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Styling
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333;
            }
            QTextEdit {
                background-color: white;
                color: #000000;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                padding: 10px;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton#btnPrint {
                background-color: #4CAF50;
                color: white;
                border: none;
            }
            QPushButton#btnPrint:hover {
                background-color: #45a049;
            }
            QPushButton#btnClose {
                background-color: #757575;
                color: white;
                border: none;
            }
            QPushButton#btnClose:hover {
                background-color: #616161;
            }
        """)
        
        # Header
        lbl_header = QLabel("📄 PREVIEW STRUK TRANSAKSI")
        lbl_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #1976D2; margin-bottom: 10px;")
        lbl_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_header)
        
        # Text Preview
        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(True)
        self.render_preview()
        layout.addWidget(self.text_preview)
        
        # Info
        lbl_info = QLabel("💡 Periksa transaksi sebelum mencetak")
        lbl_info.setStyleSheet("font-size: 10px; color: #666; font-style: italic;")
        lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_info)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_print = QPushButton("🖨️ Print & Buka PDF")
        self.btn_print.setObjectName("btnPrint")
        self.btn_print.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_print.clicked.connect(self.confirm_print)
        
        self.btn_close = QPushButton("✖️ Tutup")
        self.btn_close.setObjectName("btnClose")
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_print)
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)
        
        # Fokus ke tombol print
        self.btn_print.setFocus()
    
    def render_preview(self):
        """Render preview struk dalam format text"""
        from src.settings import load_settings
        settings = load_settings()
        nama_toko = settings.get("nama_toko", "Toko Tanpa Nama")
        alamat_toko = settings.get("alamat_toko", "")
        telepon = settings.get("telepon", "")
        
        preview_text = ""
        preview_text += "=" * 50 + "\n"
        preview_text += f"{nama_toko.center(50)}\n"
        if alamat_toko:
            preview_text += f"{alamat_toko.center(50)}\n"
        if telepon:
            preview_text += f"Telp: {telepon}".center(50) + "\n"
        preview_text += "=" * 50 + "\n\n"
        
        # Info transaksi
        preview_text += f"No. Faktur : {self.no_faktur}\n"
        preview_text += f"Tanggal    : {self.tanggal}\n"
        preview_text += f"Kasir      : {self.kasir}\n"
        preview_text += "=" * 50 + "\n\n"
        
        # Items
        subtotal_all = 0
        
        # ✅ FIX: Loop keranjang dengan format yang benar
        for item in self.keranjang:
            # item = (nama, harga, jumlah, subtotal)
            nama = item[0]
            harga = item[1]
            jumlah = item[2]
            subtotal = item[3]
            
            preview_text += f"{nama}\n"
            preview_text += f"  {jumlah} x Rp {int(harga):,}".ljust(30)
            preview_text += f"Rp {int(subtotal):,}\n\n"
            
            subtotal_all += subtotal
        
        preview_text += "-" * 50 + "\n"
            
        # Total
        preview_text += "TOTAL".ljust(30) + f"Rp {int(self.total):,}".rjust(20) + "\n"
        preview_text += "=" * 50 + "\n\n"
            
        # Pembayaran
        preview_text += "TUNAI".ljust(30) + f"Rp {int(self.uang_diterima):,}".rjust(20) + "\n"
        preview_text += "KEMBALIAN".ljust(30) + f"Rp {int(self.kembalian):,}".rjust(20) + "\n"
        preview_text += "=" * 50 + "\n"
            
        self.text_preview.setText(preview_text)
    
    def confirm_print(self):
        """User konfirmasi mau print"""
        self.user_print = True
        self.accept()
        
# --- CLASS DIALOG PEMBAYARAN ---
class DialogPembayaran(QDialog):
    def __init__(self, total_belanja, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pembayaran (Esc untuk Batal)")
        self.setFixedSize(400, 250)
        self.total_belanja = total_belanja
        self.uang_diterima = 0
        self.kembalian = 0
        self.pembayaran_sukses = False

        layout = QVBoxLayout(self)

        lbl_total = QLabel(f"Total Tagihan: Rp {int(total_belanja):,}")
        lbl_total.setStyleSheet("font-size: 18px; font-weight: bold; color: #d32f2f;")
        lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_total)

        form = QFormLayout()
        self.input_uang = QLineEdit()
        self.input_uang.setPlaceholderText("Masukkan nominal uang")
        self.input_uang.setStyleSheet("font-size: 14px; padding: 5px;")
        self.input_uang.returnPressed.connect(self.proses_bayar)
        self.input_uang.textChanged.connect(self.hitung_kembalian)
        form.addRow("Uang Diterima (Rp):", self.input_uang)
        layout.addLayout(form)

        self.lbl_kembalian = QLabel("Kembalian: Rp 0")
        self.lbl_kembalian.setStyleSheet("font-size: 16px; font-weight: bold; color: green;")
        self.lbl_kembalian.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_kembalian)

        btn_layout = QHBoxLayout()
        self.btn_batal = QPushButton("Batal (Esc)")
        self.btn_batal.setFixedHeight(40)
        self.btn_batal.clicked.connect(self.reject)
        self.btn_batal.setAutoDefault(True)

        self.btn_proses = QPushButton("PROSES BAYAR (Enter)")
        self.btn_proses.setFixedHeight(40)
        self.btn_proses.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        self.btn_proses.clicked.connect(self.proses_bayar)
        self.btn_proses.setEnabled(False)
        self.btn_proses.setAutoDefault(True)
        self.btn_proses.setDefault(True) 

        btn_layout.addWidget(self.btn_batal)
        btn_layout.addWidget(self.btn_proses)
        layout.addLayout(btn_layout)
        self.input_uang.setFocus()

    def hitung_kembalian(self):
        text = self.input_uang.text().strip().replace(".", "").replace(",", "")
        if text.isdigit():
            self.uang_diterima = int(text)
            self.kembalian = self.uang_diterima - self.total_belanja
            self.lbl_kembalian.setText(f"Kembalian: Rp {self.kembalian:,}")
            if self.kembalian >= 0:
                self.btn_proses.setEnabled(True)
                self.lbl_kembalian.setStyleSheet("font-size: 16px; font-weight: bold; color: green;")
            else:
                self.btn_proses.setEnabled(False)
                self.lbl_kembalian.setStyleSheet("font-size: 16px; font-weight: bold; color: red;")
        else:
            self.lbl_kembalian.setText("Kembalian: Rp 0")
            self.btn_proses.setEnabled(False)

    def proses_bayar(self):
        if self.btn_proses.isEnabled():
            self.pembayaran_sukses = True
            self.accept()
        else:
            self.input_uang.setFocus()

# --- CLASS DIALOG CARI BARANG ---
class DialogCariBarang(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cari Barang Manual")
        self.setGeometry(200, 200, 700, 500)
        self.selected_barcode = None

        layout = QVBoxLayout(self)
        search_layout = QHBoxLayout()
        self.input_cari = QLineEdit()
        self.input_cari.setPlaceholderText("Ketik nama barang... (Kosong = Tampilkan Semua)")
        self.input_cari.textChanged.connect(self.cari_data) 
        self.input_cari.installEventFilter(self) 
        
        btn_cari = QPushButton("Cari")
        btn_cari.clicked.connect(self.cari_data)
        
        search_layout.addWidget(self.input_cari)
        search_layout.addWidget(btn_cari)
        layout.addLayout(search_layout)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Barcode", "Nama", "Harga", "Stok"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows) 
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.itemActivated.connect(self.pilih_barang) 
        self.table.installEventFilter(self) 
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        layout.addWidget(QLabel("Gunakan Panah Bawah untuk ke tabel, Enter untuk memilih."))
        
        self.input_cari.setFocus()
        self.cari_data()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if obj == self.input_cari and event.key() == Qt.Key.Key_Down:
                if self.table.rowCount() > 0:
                    self.table.setFocus()
                    self.table.selectRow(0)
                return True
            elif obj == self.table:
                if event.key() == Qt.Key.Key_Escape:
                    self.input_cari.setFocus()
                    return True
                if event.key() == Qt.Key.Key_Up and self.table.currentRow() == 0:
                    self.input_cari.setFocus()
                    return True
        return super().eventFilter(obj, event)

    def cari_data(self):
        keyword = self.input_cari.text().strip()
        if not keyword: 
            hasil = semua_produk()
        else:
            hasil = cari_produk_by_nama_partial(keyword)
            
        self.table.setRowCount(0)
        for row, (id_prod, barcode, nama, harga, stok) in enumerate(hasil):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(barcode))
            self.table.setItem(row, 1, QTableWidgetItem(nama))
            self.table.setItem(row, 2, QTableWidgetItem(f"Rp {int(harga):,}"))
            self.table.setItem(row, 3, QTableWidgetItem(str(stok)))

    def pilih_barang(self):
        row = self.table.currentRow()
        if row >= 0:
            self.selected_barcode = self.table.item(row, 0).text()
            self.accept()

# --- CLASS DIALOG PILIH PENDING ---
class DialogPilihPending(QDialog):
    def __init__(self, daftar_pending, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pilih Transaksi Pending")
        self.setFixedSize(500, 400)
        self.daftar_pending = daftar_pending
        self.selected_index = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Styling
        self.setStyleSheet("""
            QDialog { background-color: #f5f5f5; }
            QLabel { color: #333; }
            QListWidget {
                background-color: white;
                color: #000000;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 12px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        
        # Header
        lbl_header = QLabel(f"📋 Daftar Transaksi Pending ({len(daftar_pending)})")
        lbl_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #1976D2; margin-bottom: 10px;")
        layout.addWidget(lbl_header)
        
        # List Pending
        from PyQt6.QtWidgets import QListWidget
        self.list_widget = QListWidget()
        
        for idx, pending in enumerate(daftar_pending):
            timestamp = pending['timestamp']
            total = pending['total']
            note = pending.get('note', '')
            item_count = len(pending['keranjang'])
            
            if note:
                text = f"#{idx+1} - {timestamp} - Rp {int(total):,}\n      📝 {note} ({item_count} items)"
            else:
                text = f"#{idx+1} - {timestamp} - Rp {int(total):,} ({item_count} items)"
            
            self.list_widget.addItem(text)
        
        self.list_widget.itemDoubleClicked.connect(self.recall_selected)
        layout.addWidget(self.list_widget)
        
        # Info
        lbl_info = QLabel("💡 Double-click atau pilih lalu klik Recall")
        lbl_info.setStyleSheet("font-size: 10px; color: #666; font-style: italic;")
        layout.addWidget(lbl_info)
        
        # Buttons
        btn_layout = QHBoxLayout()

        self.btn_recall = QPushButton("✅ Recall")  # ✅ TAMBAH self.
        self.btn_recall.setStyleSheet("background-color: #4CAF50; color: white; border: none;")
        self.btn_recall.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_recall.clicked.connect(self.recall_selected)
        self.btn_recall.installEventFilter(self)

        self.btn_hapus = QPushButton("🗑️ Hapus")  # ✅ TAMBAH self.
        self.btn_hapus.setStyleSheet("background-color: #f44336; color: white; border: none;")
        self.btn_hapus.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_hapus.clicked.connect(self.hapus_selected)
        self.btn_hapus.installEventFilter(self)

        self.btn_batal = QPushButton("❌ Batal")  # ✅ TAMBAH self.
        self.btn_batal.setStyleSheet("background-color: #757575; color: white; border: none;")
        self.btn_batal.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_batal.clicked.connect(self.reject)
        self.btn_batal.installEventFilter(self)

        btn_layout.addWidget(self.btn_recall)
        btn_layout.addWidget(self.btn_hapus)
        btn_layout.addWidget(self.btn_batal)
        layout.addLayout(btn_layout)
        
        self.list_widget.installEventFilter(self)
        self.list_widget.setFocus()
        if len(daftar_pending) > 0:
            self.list_widget.setCurrentRow(0)
    
    def recall_selected(self):
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            self.selected_index = current_row
            self.accept()
        else:
            QMessageBox.warning(self, "Pilih Transaksi", "Pilih transaksi yang ingin di-recall")
    
    def hapus_selected(self):
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(
                self, "Hapus Pending", 
                "Yakin hapus transaksi pending ini?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.selected_index = current_row
                self.done(2)  # Custom return code untuk hapus
        else:
            QMessageBox.warning(self, "Pilih Transaksi", "Pilih transaksi yang ingin dihapus")
        
    def eventFilter(self, obj, event):
        """Handle keyboard navigation"""
        if event.type() == QEvent.Type.KeyPress:
            
            # ===== NAVIGASI DI LIST =====
            if obj == self.list_widget:
                if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                    self.recall_selected()
                    return True
                elif event.key() == Qt.Key.Key_Delete:
                    self.hapus_selected()
                    return True
                elif event.key() == Qt.Key.Key_Escape:
                    self.reject()
                    return True
                # ✅ ARROW DOWN di list terakhir -> Pindah ke tombol pertama
                elif event.key() == Qt.Key.Key_Down:
                    if self.list_widget.currentRow() == self.list_widget.count() - 1:
                        self.btn_recall.setFocus()  # ✅ PAKAI self.
                        return True
            
            # ===== NAVIGASI DI TOMBOL =====
            # Tombol Recall
            elif obj.objectName() == "btnRecall":
                if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                    self.recall_selected()
                    return True
                elif event.key() == Qt.Key.Key_Right:
                    self.findChild(QPushButton, "btnHapus").setFocus()
                    return True
                elif event.key() == Qt.Key.Key_Up:
                    self.list_widget.setFocus()
                    return True
            
            # Tombol Hapus
            elif obj.objectName() == "btnHapus":
                if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                    self.hapus_selected()
                    return True
                elif event.key() == Qt.Key.Key_Left:
                    self.findChild(QPushButton, "btnRecall").setFocus()
                    return True
                elif event.key() == Qt.Key.Key_Right:
                    self.findChild(QPushButton, "btnBatal").setFocus()
                    return True
                elif event.key() == Qt.Key.Key_Up:
                    self.list_widget.setFocus()
                    return True
            
            # Tombol Batal
            elif obj.objectName() == "btnBatal":
                if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                    self.reject()
                    return True
                elif event.key() == Qt.Key.Key_Left:
                    self.findChild(QPushButton, "btnHapus").setFocus()
                    return True
                elif event.key() == Qt.Key.Key_Up:
                    self.list_widget.setFocus()
                    return True
        
        return super().eventFilter(obj, event)
                
# --- CLASS UTAMA KASIR ---
class KasirWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplikasi Kasir - Mode Penjualan")
        self.setGeometry(100, 100, 1100, 600)
        self.qty_shortcut = 1
     
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # --- Bagian Atas ---
        top_layout = QHBoxLayout()
        lbl_barcode = QLabel("Scan Barcode:")
        lbl_barcode.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        # ✅ TAMBAHKAN LABEL QTY SHORTCUT (Sebelum barcode input)
        self.lbl_qty_shortcut = QLabel("Qty: 1x")
        self.lbl_qty_shortcut.setFixedWidth(80)
        self.lbl_qty_shortcut.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_qty_shortcut.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #4CAF50;
                background-color: #1E1E1E;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                padding: 5px;
            }
        """)

        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Scan barcode... (Panah Bawah ke Tabel)")
        self.barcode_input.setFixedHeight(40)
        self.barcode_input.setStyleSheet("font-size: 14px; padding: 5px;")
        self.barcode_input.returnPressed.connect(self.tambah_barang_ke_keranjang)
        self.barcode_input.installEventFilter(self)
        
        self.btn_cari = QPushButton("Cari (F4)")
        self.btn_cari.setFixedHeight(40)
        self.btn_cari.setFixedWidth(80)
        self.btn_cari.clicked.connect(self.buka_dialog_cari)
        self.btn_cari.setShortcut("F4") 
        
        self.btn_qty = QPushButton("Qty (F2)")
        self.btn_qty.setFixedHeight(40)
        self.btn_qty.setFixedWidth(80)
        self.btn_qty.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold;")
        self.btn_qty.clicked.connect(self.ubah_qty_item)
        self.btn_qty.setShortcut("F2")

        self.btn_diskon = QPushButton("Disc (F8)")
        self.btn_diskon.setFixedHeight(40)
        self.btn_diskon.setFixedWidth(80)
        self.btn_diskon.setStyleSheet("background-color: #009688; color: white; font-weight: bold;")
        self.btn_diskon.clicked.connect(self.ubah_diskon_item)
        self.btn_diskon.setShortcut("F8")

        self.btn_reset = QPushButton("Reset (F5)")
        self.btn_reset.setFixedHeight(40)
        self.btn_reset.setFixedWidth(80)
        self.btn_reset.setStyleSheet("background-color: #795548; color: white; font-weight: bold;")
        self.btn_reset.clicked.connect(self.reset_keranjang_confirm)
        self.btn_reset.setShortcut("F5")
        
        self.btn_hapus = QPushButton("Hapus (Del)")
        self.btn_hapus.setFixedHeight(40)
        self.btn_hapus.setFixedWidth(90)
        self.btn_hapus.setStyleSheet("background-color: #f44336; color: white;")
        self.btn_hapus.clicked.connect(self.hapus_item_terpilih)
        self.btn_hapus.setShortcut("Delete") 

        top_layout.addWidget(lbl_barcode)
        top_layout.addWidget(self.barcode_input)
        top_layout.addWidget(self.lbl_qty_shortcut)
        top_layout.addWidget(self.btn_cari)
        top_layout.addWidget(self.btn_qty)
        top_layout.addWidget(self.btn_diskon)
        top_layout.addWidget(self.btn_reset) 
        top_layout.addWidget(self.btn_hapus)
        layout.addLayout(top_layout)

        # --- Tabel Keranjang ---
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

        # --- Bagian Bawah ---
        bottom_layout = QHBoxLayout()
        self.label_total = QLabel("Total: Rp 0")
        self.label_total.setStyleSheet("font-size: 24px; font-weight: bold; color: #2196F3;")
        
        self.btn_pending = QPushButton("Pending (F6)")
        self.btn_pending.setFixedSize(120, 60)
        self.btn_pending.setStyleSheet("background-color: #9C27B0; color: white; font-weight: bold;")
        self.btn_pending.clicked.connect(self.toggle_pending)
        
        bottom_layout.addWidget(self.btn_pending) 
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.label_total)
        
        self.btn_bayar = QPushButton("BAYAR (F12)")
        self.btn_bayar.setFixedSize(200, 60)
        self.btn_bayar.setStyleSheet("background-color: #4CAF50; color: white; font-size: 18px; font-weight: bold; border-radius: 5px;")
        self.btn_bayar.clicked.connect(self.tampilkan_dialog_bayar)
        self.btn_bayar.setShortcut("F12")
        bottom_layout.addWidget(self.btn_bayar)

        layout.addLayout(bottom_layout)

        self.keranjang_belanja = [] 
        self.daftar_pending = [] 
        self.total_transaksi = 0
        self.MAX_PENDING = 5
        self.update_pending_button()

        self.shortcut_pending = QShortcut(QKeySequence("F6"), self)
        self.shortcut_pending.activated.connect(self.toggle_pending)
        
        # [PENTING] Install Event Filter untuk ESC di window utama
        self.installEventFilter(self)

    # --- EVENT FILTER ---
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            
            # ✅ TAMBAHKAN INI (Detect angka 0-9 untuk qty shortcut)
            # Hanya aktif kalau fokus di barcode input
            if obj == self.barcode_input and not event.modifiers():
                key = event.key()
                
                # Angka 0-9
                if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
                    angka = key - Qt.Key.Key_0  # Convert key code ke angka
                    
                    # Kalau 0 -> reset ke 1
                    if angka == 0:
                        self.qty_shortcut = 1
                    else:
                        self.qty_shortcut = angka
                    
                    # Update label
                    self.update_qty_label()
                    
                    # Return True agar angka tidak masuk ke input barcode
                    return True
            
            # [PERBAIKAN UTAMA] ESCAPE -> Tutup Kasir
            if event.key() == Qt.Key.Key_Escape:
                # Cek jika keranjang ada isinya, konfirmasi dulu biar gak ke-close tidak sengaja
                if self.keranjang_belanja:
                    reply = QMessageBox.question(self, "Keluar", "Transaksi belum selesai. Yakin ingin keluar?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.Yes:
                        self.close()
                else:
                    self.close()
                return True

            # 1. Input -> Panah Bawah -> Tabel
            if obj == self.barcode_input and event.key() == Qt.Key.Key_Down:
                if self.table.rowCount() > 0:
                    self.table.setFocus()
                    self.table.selectRow(self.table.rowCount() - 1) 
                return True
            
            # 2. Tabel -> Atas (Baris 0) -> Input
            elif obj == self.table and event.key() == Qt.Key.Key_Up:
                current_row = self.table.currentRow()
                if current_row == 0: 
                    self.barcode_input.setFocus() 
                    return True
                    
        return super().eventFilter(obj, event)
    
    def update_qty_label(self):
        """Update tampilan label qty shortcut"""
        if self.qty_shortcut > 1:
            self.lbl_qty_shortcut.setText(f"Qty: {self.qty_shortcut}x")
            self.lbl_qty_shortcut.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #FF9800;
                    background-color: #1E1E1E;
                    border: 2px solid #FF9800;
                    border-radius: 5px;
                    padding: 5px;
                }
            """)
        else:
            self.lbl_qty_shortcut.setText("Qty: 1x")
            self.lbl_qty_shortcut.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #4CAF50;
                    background-color: #1E1E1E;
                    border: 2px solid #4CAF50;
                    border-radius: 5px;
                    padding: 5px;
                }
            """)

    def toggle_pending(self):
        """Toggle antara Pending (simpan) dan Recall (ambil kembali)"""
        
        # CASE 1: Ada keranjang aktif -> PENDING (SIMPAN)
        if self.keranjang_belanja:
            # Cek apakah sudah max pending
            if len(self.daftar_pending) >= self.MAX_PENDING:
                QMessageBox.warning(
                    self, "Pending Penuh", 
                    f"Maksimal {self.MAX_PENDING} transaksi pending.\n"
                    "Selesaikan transaksi pending lama terlebih dahulu."
                )
                self.barcode_input.setFocus()
                return
            
            # Input note (opsional)
            note, ok = QInputDialog.getText(
                self, "Catatan Pending", 
                "Catatan (opsional, misal: 'Ibu baju merah'):",
                QLineEdit.EchoMode.Normal
            )
            
            if not ok:  # User cancel
                self.barcode_input.setFocus()
                return
            
            # Simpan ke daftar pending
            pending_data = {
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'note': note.strip(),
                'total': self.total_transaksi,
                'keranjang': list(self.keranjang_belanja)  # Copy list
            }
            
            self.daftar_pending.append(pending_data)
            
            # Reset keranjang aktif
            self.keranjang_belanja = []
            self.update_tabel_dan_total()
            
            # Update tombol
            self.update_pending_button()
            
            QMessageBox.information(
                self, "Pending Tersimpan", 
                f"Transaksi disimpan!\n\n"
                f"Total Pending: {len(self.daftar_pending)}\n"
                f"Note: {note if note else '-'}"
            )
            
            self.barcode_input.setFocus()
    
        # CASE 2: Tidak ada keranjang aktif -> RECALL (AMBIL)
        elif self.daftar_pending:
            # Tampilkan dialog pilih pending
            dialog = DialogPilihPending(self.daftar_pending, self)
            result = dialog.exec()
            
            if result == QDialog.DialogCode.Accepted:  # Recall
                idx = dialog.selected_index
                if idx is not None:
                    # Ambil data pending
                    pending = self.daftar_pending[idx]
                    self.keranjang_belanja = list(pending['keranjang'])
                    self.update_tabel_dan_total()
                    
                    # Hapus dari daftar pending
                    self.daftar_pending.pop(idx)
                    self.update_pending_button()
                    
                    QMessageBox.information(
                        self, "Recall Berhasil", 
                        f"Transaksi di-recall!\n\n"
                        f"Note: {pending.get('note', '-')}\n"
                        f"Total: Rp {int(pending['total']):,}"
                    )
            
            elif result == 2:  # Hapus (custom code)
                idx = dialog.selected_index
                if idx is not None:
                    self.daftar_pending.pop(idx)
                    self.update_pending_button()
                    QMessageBox.information(self, "Dihapus", "Transaksi pending dihapus")
            
            self.barcode_input.setFocus()
    
        # CASE 3: Tidak ada apa-apa
        else:
            QMessageBox.information(self, "Info", "Tidak ada transaksi untuk di-pending atau di-recall")
            self.barcode_input.setFocus()

    def update_pending_button(self):
        """Update tampilan tombol pending berdasarkan jumlah pending"""
        count = len(self.daftar_pending)
        
        if count == 0:
            self.btn_pending.setText("Pending (F6)")
            self.btn_pending.setStyleSheet("background-color: #9C27B0; color: white; font-weight: bold;")
        else:
            self.btn_pending.setText(f"Pending ({count}) F6")
            self.btn_pending.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold;")
            
    def ubah_qty_item(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Pilih Item", "Pilih item di tabel dulu!")
            return

        item = self.keranjang_belanja[row]
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT stok FROM produk WHERE id = ?", (item['id'],))
        res = cursor.fetchone()
        conn.close()
        stok_db = res[0] if res else 0

        qty_baru, ok = QInputDialog.getInt(self, "Ubah Jumlah", f"Stok: {stok_db}\nJumlah baru:", value=item['qty'], min=1, max=10000)
        if ok:
            if qty_baru > stok_db:
                QMessageBox.critical(self, "Stok Kurang", f"Stok hanya ada {stok_db}!")
            else:
                self.keranjang_belanja[row]['qty'] = qty_baru
                self.update_tabel_dan_total()
                self.barcode_input.setFocus()

    def ubah_diskon_item(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Pilih Item", "Pilih item di tabel dulu!")
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

    def reset_keranjang_confirm(self):
        if not self.keranjang_belanja: return
        reply = QMessageBox.question(self, "Batal Transaksi", "Kosongkan keranjang?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.reset_keranjang()

    def hapus_item_terpilih(self):
        row = self.table.currentRow()
        if row >= 0:
            nama = self.keranjang_belanja[row]['nama']
            reply = QMessageBox.question(self, "Hapus", f"Hapus '{nama}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                del self.keranjang_belanja[row]
                self.update_tabel_dan_total()
                self.barcode_input.setFocus()
        else:
            QMessageBox.warning(self, "Pilih Item", "Pilih item yang ingin dihapus.")

    def buka_dialog_cari(self):
        dialog = DialogCariBarang(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.selected_barcode:
                self.barcode_input.setText(dialog.selected_barcode)
                self.tambah_barang_ke_keranjang()

    def tambah_barang_ke_keranjang(self):
        barcode = self.barcode_input.text().strip()
        if not barcode: return
        produk = cari_produk_dari_barcode(barcode)
        
        if produk:
            id_produk, nama, harga, stok_db = produk
            if stok_db <= 0:
                 QMessageBox.warning(self, "Stok Habis", f"Stok '{nama}' kosong!")
                 self.barcode_input.clear()
                 return
             
             # ✅ CEK STOK DENGAN QTY SHORTCUT
            if self.qty_shortcut > stok_db:
                QMessageBox.warning(self, "Stok Kurang", 
                    f"Stok hanya {stok_db}, tidak cukup untuk {self.qty_shortcut} pcs!")
                self.barcode_input.clear()
                self.qty_shortcut = 1  # Reset
                self.update_qty_label()
                return
        
            item_found = False
            for item in self.keranjang_belanja:
                if item['id'] == id_produk:
                    # ✅ TAMBAH SESUAI QTY SHORTCUT
                    if item['qty'] + self.qty_shortcut > stok_db:
                        QMessageBox.warning(self, "Stok Habis", f"Sisa stok hanya {stok_db}.")
                        self.barcode_input.clear()
                        self.qty_shortcut = 1
                        self.update_qty_label()
                        return
                    
                    item['qty'] += self.qty_shortcut  # ✅ GANTI INI
                    item_found = True
                    break
                
            if not item_found:
                self.keranjang_belanja.append({
                    'id': id_produk, 'nama': nama, 'harga': harga, 
                    'qty': self.qty_shortcut,  # ✅ GANTI INI
                    'diskon': 0, 'subtotal': harga * self.qty_shortcut
                })
                
            self.update_tabel_dan_total()
            self.qty_shortcut = 1
            self.update_qty_label()
            
        else:
            reply = QMessageBox.question(self, "404", f"Barcode '{barcode}' tidak ada.\nCari manual?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.buka_dialog_cari()
        self.barcode_input.clear()
        self.barcode_input.setFocus()

    def update_tabel_dan_total(self):
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

    def tampilkan_dialog_bayar(self):
        if not self.keranjang_belanja:
            QMessageBox.warning(self, "Kosong", "Keranjang kosong.")
            return
        dialog = DialogPembayaran(self.total_transaksi, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.pembayaran_sukses:
            self.simpan_transaksi(dialog.uang_diterima, dialog.kembalian)

    def simpan_transaksi(self, uang_diterima, kembalian):
        conn = create_connection()
        cursor = conn.cursor()
        try:
            from src.database import generate_nomor_faktur
            no_faktur = generate_nomor_faktur()
        
            tanggal_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO transaksi (no_faktur, tanggal, total) VALUES (?, ?, ?)", (no_faktur, tanggal_sekarang, self.total_transaksi))
            transaksi_id = cursor.lastrowid
            
            for item in self.keranjang_belanja:
                nilai_diskon = item.get('diskon', 0)
                cursor.execute("""
                    INSERT INTO detail_transaksi (transaksi_id, produk_nama, jumlah, harga, diskon, subtotal) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (transaksi_id, item['nama'], item['qty'], item['harga'], nilai_diskon, item['subtotal']))
                cursor.execute("UPDATE produk SET stok = stok - ? WHERE id = ?", (item['qty'], item['id']))
            
            conn.commit()
            
            from src.database import log_aktivitas_pengguna
            username = getattr(self, 'current_user', 'admin')
            log_aktivitas_pengguna(username, "Transaksi Penjualan", f"ID: {transaksi_id}, Total: Rp {self.total_transaksi}")

            # Siapkan data struk
            data_struk = []
            for item in self.keranjang_belanja:
                data_struk.append((item['nama'], int(item['harga']), item['qty'], int(item['subtotal'])))
            
            # ✅ CETAK STRUK DULU (SEBELUM PREVIEW)
            filepath = None
            try:
                filepath = cetak_struk_pdf(
                    NAMA_TOKO, 
                    ALAMAT_TOKO, 
                    data_struk, 
                    int(self.total_transaksi),
                    no_faktur,
                    uang_diterima,
                    kembalian,
                    username
                )
            except Exception as e:
                print(f"Error cetak struk: {e}")
                
            # ✅ TAMPILKAN PREVIEW DIALOG
            tanggal_str = datetime.now().strftime('%d/%m/%Y %H:%M')
            preview_dialog = DialogPreviewStruk(
                no_faktur=no_faktur,
                tanggal=tanggal_str,
                kasir=username,
                keranjang=data_struk,
                total=self.total_transaksi,
                uang_diterima=uang_diterima,
                kembalian=kembalian,
                parent=self
            )
            
            # Tunggu user pilih Print atau Tutup
            if preview_dialog.exec() == QDialog.DialogCode.Accepted and preview_dialog.user_print:
                # User klik Print -> Cetak PDF
                if filepath:
                    try:
                        import os, platform
                        if platform.system() == 'Windows': 
                            os.startfile(filepath)
                    except Exception as e:
                        print(f"Gagal buka PDF: {e}")
                
                QMessageBox.information(self, "Berhasil", 
                    f"✅ Transaksi berhasil!\n\n"
                    f"Bayar: Rp {int(uang_diterima):,}\n"
                    f"Kembali: Rp {int(kembalian):,}")
            else:
                # User klik Tutup -> Struk sudah dibuat, tapi tidak dibuka
                QMessageBox.information(self, "Transaksi Berhasil", 
                    f"✅ Transaksi tersimpan\n\n"
                    f"No. Faktur: {no_faktur}\n"
                    f"Total: Rp {int(self.total_transaksi):,}\n\n"
                    f"Struk tersimpan di folder 'struk'")
            
            self.reset_keranjang()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Error", f"Gagal simpan: {str(e)}")
        finally:
            conn.close()

    def reset_keranjang(self):
        self.keranjang_belanja = []
        self.total_transaksi = 0
        self.update_tabel_dan_total()
        self.barcode_input.setFocus()

    def set_current_user(self, username):
        self.current_user = username