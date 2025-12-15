"""
Riwayat Hari Ini Window - REFACTORED VERSION
=============================================
Menggunakan BaseWindow untuk konsistensi
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QFrame, QFileDialog
)
from PyQt6.QtCore import Qt
from datetime import datetime

from src.ui.base.base_window import BaseWindow
from src.ui.base.style_manager import StyleManager
from src.database import create_connection

class RiwayatHariIniWindow(BaseWindow):
    """
    Window riwayat transaksi hari ini
    
    Features:
    - Display transaksi hari ini
    - Detail transaksi
    - Print ulang struk
    - Export PDF
    """
    
    def __init__(self):
        super().__init__()
        
        self.setup_ui()
        self.setup_navigation()
        self.muat_riwayat()
        
        # Window properties
        self.setWindowTitle("Riwayat Transaksi Hari Ini")
        self.setGeometry(100, 100, 1000, 600)
    
    def setup_ui(self):
        """Setup UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #181818; 
                border-radius: 8px; 
                border: 1px solid #333;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 15, 15, 15)
        
        tanggal_hari_ini = datetime.now().strftime("%d %B %Y")
        lbl_title = QLabel(f"📊 RIWAYAT TRANSAKSI HARI INI")
        lbl_title.setStyleSheet("font-size: 18px; color: #2196F3; font-weight: bold;")
        
        self.lbl_tanggal = QLabel(f"Tanggal: {tanggal_hari_ini}")
        self.lbl_tanggal.setStyleSheet("font-size: 12px; color: #aaa;")
        
        self.lbl_summary = QLabel("Loading...")
        self.lbl_summary.setStyleSheet("font-size: 14px; color: #4CAF50; font-weight: bold; margin-top: 5px;")
        
        header_layout.addWidget(lbl_title)
        header_layout.addWidget(self.lbl_tanggal)
        header_layout.addWidget(self.lbl_summary)
        
        layout.addWidget(header_frame)
        
        # Table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "No. Faktur", "Jam", "Kasir", "Total", "Aksi"])
        self.table.setColumnHidden(0, True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget { alternate-background-color: #252525; }")
        self.table.installEventFilter(self)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.table)
        
        # Tombol Aksi
        btn_layout = QHBoxLayout()
        
        style = StyleManager()
        
        self.btn_detail = QPushButton("📄 Detail Transaksi")
        self.btn_detail.setStyleSheet(style.get_button_style('default'))
        self.btn_detail.clicked.connect(self.lihat_detail)
        self.btn_detail.installEventFilter(self)
        
        self.btn_print = QPushButton("🖨️ Print Ulang")
        self.btn_print.setStyleSheet(style.get_button_style('default'))
        self.btn_print.clicked.connect(self.print_ulang)
        self.btn_print.installEventFilter(self)
        
        self.btn_export = QPushButton("📥 Export PDF")
        self.btn_export.setStyleSheet(style.get_button_style('success'))
        self.btn_export.clicked.connect(self.export_pdf)
        self.btn_export.installEventFilter(self)
        
        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.setStyleSheet(style.get_button_style('default'))
        self.btn_refresh.clicked.connect(self.muat_riwayat)
        self.btn_refresh.installEventFilter(self)
        
        btn_layout.addWidget(self.btn_detail)
        btn_layout.addWidget(self.btn_print)
        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # Info navigasi
        lbl_nav = QLabel("Navigasi: Arrow Keys | Enter (Detail) | ESC (Tutup)")
        lbl_nav.setStyleSheet("color: #777; font-size: 11px; font-style: italic;")
        layout.addWidget(lbl_nav)
        
        # Initial focus
        self.table.setFocus()
    
    def setup_navigation(self):
        """Setup keyboard navigation"""
        # Table: Enter = detail
        self.register_navigation(self.table, {
            Qt.Key.Key_Return: self.lihat_detail
        })
        
        # Tombol Detail
        self.register_navigation(self.btn_detail, {
            Qt.Key.Key_Return: self.lihat_detail,
            Qt.Key.Key_Right: self.btn_print,
            Qt.Key.Key_Up: lambda: self.focus_table_last_row(self.table)
        })
        
        # Tombol Print
        self.register_navigation(self.btn_print, {
            Qt.Key.Key_Return: self.print_ulang,
            Qt.Key.Key_Left: self.btn_detail,
            Qt.Key.Key_Right: self.btn_export,
            Qt.Key.Key_Up: lambda: self.focus_table_last_row(self.table)
        })
        
        # Tombol Export
        self.register_navigation(self.btn_export, {
            Qt.Key.Key_Return: self.export_pdf,
            Qt.Key.Key_Left: self.btn_print,
            Qt.Key.Key_Right: self.btn_refresh,
            Qt.Key.Key_Up: lambda: self.focus_table_last_row(self.table)
        })
        
        # Tombol Refresh
        self.register_navigation(self.btn_refresh, {
            Qt.Key.Key_Return: self.muat_riwayat,
            Qt.Key.Key_Left: self.btn_export,
            Qt.Key.Key_Up: lambda: self.focus_table_last_row(self.table)
        })
    
    def eventFilter(self, obj, event):
        """Handle special keyboard events"""
        from PyQt6.QtCore import QEvent
        
        if event.type() == QEvent.Type.KeyPress:
            # Table: Down di baris terakhir = pindah ke tombol
            if obj == self.table:
                if event.key() == Qt.Key.Key_Down:
                    if self.table.currentRow() == self.table.rowCount() - 1:
                        self.btn_detail.setFocus()
                        return True
        
        return super().eventFilter(obj, event)
    
    def muat_riwayat(self):
        """Muat transaksi hari ini dari database"""
        self.table.setRowCount(0)
        
        conn = create_connection()
        cursor = conn.cursor()
        
        tanggal_hari_ini = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute("""
            SELECT id, no_faktur, tanggal, total 
            FROM transaksi 
            WHERE DATE(tanggal) = ?
            ORDER BY tanggal DESC
        """, (tanggal_hari_ini,))
        
        transaksi_list = cursor.fetchall()
        conn.close()
        
        total_omset = 0
        
        for row, (trans_id, no_faktur, tanggal, total) in enumerate(transaksi_list):
            self.table.insertRow(row)
            
            jam = datetime.strptime(tanggal, "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S")
            
            self.table.setItem(row, 0, QTableWidgetItem(str(trans_id)))
            self.table.setItem(row, 1, QTableWidgetItem(no_faktur if no_faktur else "-"))
            self.table.setItem(row, 2, QTableWidgetItem(jam))
            self.table.setItem(row, 3, QTableWidgetItem("admin"))
            
            item_total = QTableWidgetItem(f"Rp {int(total):,}")
            item_total.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 4, item_total)
            
            self.table.setItem(row, 5, QTableWidgetItem(""))
            
            total_omset += total
        
        # Update summary
        self.lbl_summary.setText(
            f"Total: {len(transaksi_list)} transaksi | "
            f"Omset: Rp {int(total_omset):,}"
        )
    
    def lihat_detail(self):
        """Tampilkan detail transaksi"""
        row = self.table.currentRow()
        if row < 0:
            self.show_warning("Pilih Transaksi", "Pilih transaksi yang ingin dilihat")
            return
        
        trans_id = int(self.table.item(row, 0).text())
        no_faktur = self.table.item(row, 1).text()
        
        # Ambil detail
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT produk_nama, jumlah, harga, diskon, subtotal
            FROM detail_transaksi
            WHERE transaksi_id = ?
        """, (trans_id,))
        
        items = cursor.fetchall()
        conn.close()
        
        # Format pesan
        pesan = f"Detail Transaksi: {no_faktur}\n\n"
        pesan += "=" * 50 + "\n"
        
        for nama, jumlah, harga, diskon, subtotal in items:
            pesan += f"{nama}\n"
            pesan += f"  {jumlah} x Rp {int(harga):,}"
            if diskon > 0:
                pesan += f" (Disc: Rp {int(diskon):,})"
            pesan += f" = Rp {int(subtotal):,}\n\n"
        
        pesan += "=" * 50
        
        self.show_success("Detail Transaksi", pesan)
    
    def print_ulang(self):
        """Print ulang struk"""
        row = self.table.currentRow()
        if row < 0:
            self.show_warning("Pilih Transaksi", "Pilih transaksi yang ingin di-print ulang")
            return
        
        trans_id = int(self.table.item(row, 0).text())
        no_faktur = self.table.item(row, 1).text()
        
        # Ambil data lengkap
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT tanggal, total FROM transaksi WHERE id = ?", (trans_id,))
        tanggal, total = cursor.fetchone()
        
        cursor.execute("""
            SELECT produk_nama, harga, jumlah, subtotal
            FROM detail_transaksi
            WHERE transaksi_id = ?
        """, (trans_id,))
        
        items = cursor.fetchall()
        conn.close()
        
        # Generate struk
        try:
            from src.cetak_struk import cetak_struk_pdf
            from src.config import NAMA_TOKO, ALAMAT_TOKO
            
            filepath = cetak_struk_pdf(
                NAMA_TOKO, ALAMAT_TOKO, items, int(total),
                no_faktur, 0, 0, "admin"
            )
            
            # Buka PDF
            import os, platform
            if platform.system() == 'Windows':
                os.startfile(filepath)
            
            self.show_success("Berhasil", "Struk berhasil di-print ulang!")
            
        except Exception as e:
            self.show_error("Error", f"Gagal print ulang:\n{e}")
    
    def export_pdf(self):
        """Export semua transaksi hari ini ke PDF"""
        if self.table.rowCount() == 0:
            self.show_warning("Tidak Ada Data", "Tidak ada transaksi hari ini")
            return
        
        tanggal_str = datetime.now().strftime("%Y%m%d")
        default_filename = f"riwayat_transaksi_{tanggal_str}.pdf"
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Simpan PDF", default_filename, "PDF Files (*.pdf)"
        )
        
        if not filepath:
            return
        
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
            
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Header
            tanggal_lengkap = datetime.now().strftime("%d %B %Y")
            story.append(Paragraph(f"<b>RIWAYAT TRANSAKSI HARI INI</b>", styles['Title']))
            story.append(Paragraph(f"Tanggal: {tanggal_lengkap}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Data tabel
            data = [["No", "No. Faktur", "Jam", "Total"]]
            
            total_omset = 0
            for row in range(self.table.rowCount()):
                no = row + 1
                no_faktur = self.table.item(row, 1).text()
                jam = self.table.item(row, 2).text()
                total_text = self.table.item(row, 4).text()
                
                data.append([str(no), no_faktur, jam, total_text])
                
                total_angka = int(total_text.replace("Rp ", "").replace(",", "").replace(".", ""))
                total_omset += total_angka
            
            data.append(["", "", "TOTAL", f"Rp {total_omset:,}"])
            
            # Buat tabel
            table = Table(data, colWidths=[50, 150, 100, 150])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ]))
            
            story.append(table)
            doc.build(story)
            
            self.show_success("Berhasil", f"PDF tersimpan:\n{filepath}")
            
        except Exception as e:
            self.show_error("Error", f"Gagal export PDF:\n{e}")