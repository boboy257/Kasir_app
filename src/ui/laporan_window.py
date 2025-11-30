from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QFileDialog, QHeaderView
)
from PyQt6.QtCore import Qt
import csv
from datetime import datetime
from pathlib import Path
from src.database import create_connection

class LaporanWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Laporan Penjualan")
        self.setGeometry(100, 100, 1000, 600)

        # Buat folder export jika belum ada
        self.export_folder = Path("export")
        self.export_folder.mkdir(exist_ok=True)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Tombol refresh dan export
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh Data")
        self.btn_refresh.clicked.connect(self.muat_laporan)
        btn_layout.addWidget(self.btn_refresh)

        self.btn_export_csv = QPushButton("Export ke CSV")
        self.btn_export_csv.clicked.connect(self.export_csv)
        btn_layout.addWidget(self.btn_export_csv)

        self.btn_export_pdf = QPushButton("Export ke PDF")
        self.btn_export_pdf.clicked.connect(self.export_pdf)
        btn_layout.addWidget(self.btn_export_pdf)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # [UBAH] Tambah Kolom Diskon (Total 6 Kolom)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Tanggal", "Nama Produk", "Jumlah", "Harga", "Disc", "Subtotal"])
        
        # Atur lebar kolom
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) # Nama produk melar
        self.table.setColumnWidth(0, 150) # Tanggal
        self.table.setColumnWidth(2, 60)  # Qty
        self.table.setColumnWidth(3, 100) # Harga
        self.table.setColumnWidth(4, 80)  # Disc
        self.table.setColumnWidth(5, 120) # Subtotal
        
        layout.addWidget(self.table)

        self.muat_laporan()

    def muat_laporan(self):
        self.table.setRowCount(0)
        conn = create_connection()
        cursor = conn.cursor()

        # [UBAH] Query ambil kolom diskon juga
        cursor.execute("""
            SELECT t.tanggal, dt.produk_nama, dt.jumlah, dt.harga, dt.diskon, dt.subtotal
            FROM transaksi t
            JOIN detail_transaksi dt ON t.id = dt.transaksi_id
            ORDER BY t.tanggal DESC
        """)
        hasil = cursor.fetchall()
        conn.close()

        # Isi tabel
        for row, (tanggal, nama, jumlah, harga, diskon, subtotal) in enumerate(hasil):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(tanggal))
            self.table.setItem(row, 1, QTableWidgetItem(nama))
            self.table.setItem(row, 2, QTableWidgetItem(str(jumlah)))
            self.table.setItem(row, 3, QTableWidgetItem(f"Rp {int(harga):,}"))
            
            # Kolom Diskon (Handle kalau None)
            val_diskon = int(diskon) if diskon else 0
            self.table.setItem(row, 4, QTableWidgetItem(f"Rp {val_diskon:,}"))
            
            self.table.setItem(row, 5, QTableWidgetItem(f"Rp {int(subtotal):,}"))

    def export_csv(self):
        conn = create_connection()
        cursor = conn.cursor()
        # [UBAH] Query export diskon juga
        cursor.execute("""
            SELECT t.tanggal, dt.produk_nama, dt.jumlah, dt.harga, dt.diskon, dt.subtotal
            FROM transaksi t
            JOIN detail_transaksi dt ON t.id = dt.transaksi_id
            ORDER BY t.tanggal DESC
        """)
        hasil = cursor.fetchall()
        conn.close()

        if not hasil:
            QMessageBox.warning(self, "Kosong", "Tidak ada data.")
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Simpan CSV", str(self.export_folder / "laporan.csv"), "CSV (*.csv)")
        if not filename: return

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # [UBAH] Header CSV
                writer.writerow(["Tanggal", "Nama Produk", "Jumlah", "Harga", "Diskon", "Subtotal"])
                writer.writerows(hasil)
            QMessageBox.information(self, "Berhasil", f"Data diexport ke:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def export_pdf(self):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.tanggal, dt.produk_nama, dt.jumlah, dt.harga, dt.diskon, dt.subtotal
            FROM transaksi t
            JOIN detail_transaksi dt ON t.id = dt.transaksi_id
            ORDER BY t.tanggal DESC
        """)
        hasil = cursor.fetchall()
        conn.close()

        if not hasil:
            QMessageBox.warning(self, "Kosong", "Tidak ada data.")
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Simpan PDF", str(self.export_folder / "laporan.pdf"), "PDF (*.pdf)")
        if not filename: return

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors

            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []

            story.append(Paragraph("Laporan Penjualan", styles['Title']))
            story.append(Spacer(1, 12))

            # [UBAH] Data Tabel PDF
            data = [["Tanggal", "Produk", "Qty", "Harga", "Disc", "Subtotal"]]
            for row in hasil:
                disc = int(row[4]) if row[4] else 0
                data.append([
                    row[0],             # Tanggal
                    row[1],             # Nama
                    str(row[2]),        # Qty
                    f"{int(row[3]):,}", # Harga
                    f"{disc:,}",        # Diskon
                    f"{int(row[5]):,}"  # Subtotal
                ])

            table = Table(data)
            # Style tabel PDF
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(table)
            doc.build(story)
            QMessageBox.information(self, "Berhasil", f"PDF tersimpan di:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal PDF: {str(e)}\nPastikan pip install reportlab sudah dilakukan.")
            
    def set_current_user(self, username):
        self.current_user = username