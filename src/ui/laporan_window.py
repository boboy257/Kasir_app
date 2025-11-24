from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt
import csv
from datetime import datetime
from pathlib import Path
from src.database import create_connection

# Tambahkan import untuk PDF jika belum ada
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
except ImportError:
    pass

class LaporanWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Laporan Penjualan")
        self.setGeometry(100, 100, 1000, 600)

        # Buat folder export jika belum ada (saat aplikasi dibuka)
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

        # Tabel laporan
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Tanggal", "Nama Produk", "Jumlah", "Harga", "Subtotal"])
        layout.addWidget(self.table)

        # Muat data awal
        self.muat_laporan()

    def muat_laporan(self):
        # Kosongkan tabel
        self.table.setRowCount(0)

        # Ambil data dari database
        conn = create_connection()
        cursor = conn.cursor()

        # Query untuk ambil data laporan
        cursor.execute("""
            SELECT t.tanggal, dt.produk_nama, dt.jumlah, dt.harga, dt.subtotal
            FROM transaksi t
            JOIN detail_transaksi dt ON t.id = dt.transaksi_id
            ORDER BY t.tanggal DESC
        """)
        hasil = cursor.fetchall()
        conn.close()

        # Isi tabel
        for row, (tanggal, nama, jumlah, harga, subtotal) in enumerate(hasil):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(tanggal))
            self.table.setItem(row, 1, QTableWidgetItem(nama))
            self.table.setItem(row, 2, QTableWidgetItem(str(jumlah)))
            self.table.setItem(row, 3, QTableWidgetItem(f"Rp {harga}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"Rp {subtotal}"))

    def export_csv(self):
        # Ambil data dari database
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.tanggal, dt.produk_nama, dt.jumlah, dt.harga, dt.subtotal
            FROM transaksi t
            JOIN detail_transaksi dt ON t.id = dt.transaksi_id
            ORDER BY t.tanggal DESC
        """)
        hasil = cursor.fetchall()
        conn.close()

        if not hasil:
            QMessageBox.warning(self, "Tidak Ada Data", "Tidak ada data untuk diexport.")
            return

        # Nama file default dengan timestamp
        default_filename = f"laporan_penjualan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        # Simpan file ke folder export
        default_path = self.export_folder / default_filename

        # Pilih lokasi file
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan Laporan ke CSV",
            str(default_path),  # Gunakan path default ke folder export
            "CSV Files (*.csv)"
        )

        if not filename:
            return

        # Simpan ke CSV
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Tanggal", "Nama Produk", "Jumlah", "Harga", "Subtotal"])
                writer.writerows(hasil)
            QMessageBox.information(self, "Export Berhasil", f"Data berhasil diexport ke:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal export CSV:\n{str(e)}")

    def export_pdf(self):
        # Ambil data dari database
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.tanggal, dt.produk_nama, dt.jumlah, dt.harga, dt.subtotal
            FROM transaksi t
            JOIN detail_transaksi dt ON t.id = dt.transaksi_id
            ORDER BY t.tanggal DESC
        """)
        hasil = cursor.fetchall()
        conn.close()

        if not hasil:
            QMessageBox.warning(self, "Tidak Ada Data", "Tidak ada data untuk diexport.")
            return

        # Nama file default dengan timestamp
        default_filename = f"laporan_penjualan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        # Simpan file ke folder export
        default_path = self.export_folder / default_filename

        # Pilih lokasi file
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan Laporan ke PDF",
            str(default_path),  # Gunakan path default ke folder export
            "PDF Files (*.pdf)"
        )

        if not filename:
            return

        # Gunakan reportlab untuk buat PDF
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors

            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []

            # Judul
            judul = Paragraph("Laporan Penjualan", styles['Title'])
            story.append(judul)
            story.append(Spacer(1, 12))

            # Header tabel
            data = [["Tanggal", "Nama Produk", "Jumlah", "Harga", "Subtotal"]]
            for row in hasil:
                data.append([row[0], row[1], str(row[2]), f"Rp {row[3]}", f"Rp {row[4]}"])

            # Buat tabel
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(table)
            doc.build(story)

            QMessageBox.information(self, "Export Berhasil", f"Data berhasil diexport ke:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal export PDF:\n{str(e)}")