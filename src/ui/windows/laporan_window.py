"""
Laporan Window - REFACTORED VERSION
====================================
Menggunakan BaseWindow untuk konsistensi
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLabel, QDateEdit, QFrame,
    QAbstractItemView, QHeaderView, QFileDialog
)
from PyQt6.QtCore import Qt, QDate, QEvent
import csv
from datetime import datetime
from pathlib import Path

from src.ui.base.base_window import BaseWindow
from src.ui.base.style_manager import StyleManager
from src.database import ambil_laporan_filter

class LaporanWindow(BaseWindow):
    """
    Window untuk laporan penjualan
    
    Features:
    - Filter by date range
    - Export to CSV/PDF
    - Total omset calculation
    """
    
    def __init__(self):
        super().__init__()
        
        self.export_folder = Path("export")
        self.export_folder.mkdir(exist_ok=True)
        
        self.setup_ui()
        self.setup_navigation()
        
        # Window properties
        self.setWindowTitle("Laporan Penjualan")
        self.setGeometry(100, 100, 1100, 700)
        
        # Load data
        self.muat_laporan()
    
    def setup_ui(self):
        """Setup UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ===== FILTER AREA =====
        filter_frame = QFrame()
        filter_frame.setStyleSheet(
            "background-color: #181818; border-radius: 8px; border: 1px solid #333;"
        )
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(15, 15, 15, 15)
        filter_layout.setSpacing(10)
        
        # Date filters
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDisplayFormat("yyyy-MM-dd")
        self.date_start.setDate(QDate.currentDate())
        
        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDisplayFormat("yyyy-MM-dd")
        self.date_end.setDate(QDate.currentDate())
        
        # Buttons
        style = StyleManager()
        
        self.btn_filter = QPushButton("Terapkan Filter")
        self.btn_filter.setStyleSheet(style.get_button_style('primary'))
        self.btn_filter.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_filter.clicked.connect(self.muat_laporan)
        
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self.reset_filter)
        
        self.btn_csv = QPushButton("Export CSV")
        self.btn_csv.setStyleSheet(style.get_button_style('success'))
        self.btn_csv.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_csv.clicked.connect(self.export_csv)
        
        self.btn_pdf = QPushButton("Export PDF")
        self.btn_pdf.setStyleSheet(style.get_button_style('danger'))
        self.btn_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pdf.clicked.connect(self.export_pdf)
        
        # Layout
        filter_layout.addWidget(QLabel("Dari:"))
        filter_layout.addWidget(self.date_start)
        filter_layout.addWidget(QLabel("Sampai:"))
        filter_layout.addWidget(self.date_end)
        filter_layout.addWidget(self.btn_filter)
        filter_layout.addWidget(self.btn_reset)
        filter_layout.addStretch()
        filter_layout.addWidget(self.btn_csv)
        filter_layout.addWidget(self.btn_pdf)
        
        layout.addWidget(filter_frame)
        
        # ===== TABLE =====
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "Tanggal", "Nama Produk", "Jumlah", "Harga", "Disc", "Subtotal"
        ])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget { alternate-background-color: #252525; }")
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(2, 60)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 120)
        
        layout.addWidget(self.table)
        
        # ===== FOOTER =====
        footer_layout = QHBoxLayout()
        
        self.lbl_total_periode = QLabel("Total Omset Periode Ini: Rp 0")
        self.lbl_total_periode.setStyleSheet(
            "font-size: 18px; color: #00E5FF; font-weight: bold;"
        )
        
        footer_layout.addStretch()
        footer_layout.addWidget(self.lbl_total_periode)
        layout.addLayout(footer_layout)
        
        # Focus awal
        self.date_start.setFocus()
    
    def setup_navigation(self):
        """Setup keyboard navigation"""
        
        # Date Start: Enter = next field
        self.register_navigation(self.date_start, {
            Qt.Key.Key_Return: self.date_end,
            Qt.Key.Key_Down: lambda: self.focus_table_first_row(self.table)
        })
        
        # Date End: Enter = filter button
        self.register_navigation(self.date_end, {
            Qt.Key.Key_Return: self.btn_filter,
            Qt.Key.Key_Down: lambda: self.focus_table_first_row(self.table)
        })
        
        # Button Filter
        self.register_navigation(self.btn_filter, {
            Qt.Key.Key_Return: self.muat_laporan,
            Qt.Key.Key_Right: self.btn_reset,
            Qt.Key.Key_Left: self.date_end,
            Qt.Key.Key_Down: lambda: self.focus_table_first_row(self.table)
        })
        
        # Button Reset
        self.register_navigation(self.btn_reset, {
            Qt.Key.Key_Return: self.reset_filter,
            Qt.Key.Key_Right: self.btn_csv,
            Qt.Key.Key_Left: self.btn_filter,
            Qt.Key.Key_Down: lambda: self.focus_table_first_row(self.table)
        })
        
        # Button CSV
        self.register_navigation(self.btn_csv, {
            Qt.Key.Key_Return: self.export_csv,
            Qt.Key.Key_Right: self.btn_pdf,
            Qt.Key.Key_Left: self.btn_reset,
            Qt.Key.Key_Down: lambda: self.focus_table_first_row(self.table)
        })
        
        # Button PDF
        self.register_navigation(self.btn_pdf, {
            Qt.Key.Key_Return: self.export_pdf,
            Qt.Key.Key_Left: self.btn_csv,
            Qt.Key.Key_Down: lambda: self.focus_table_first_row(self.table)
        })
    
    def eventFilter(self, obj, event):
        """Handle table navigation"""
        if event.type() == QEvent.Type.KeyPress:
            
            # Table: Up di baris 0 = balik ke filter
            if obj == self.table:
                if event.key() == Qt.Key.Key_Up and self.table.currentRow() <= 0:
                    self.btn_filter.setFocus()
                    return True
        
        return super().eventFilter(obj, event)
    
    # ========== DATA OPERATIONS ==========
    
    def muat_laporan(self):
        """Load laporan berdasarkan date range"""
        start_date = self.date_start.date().toString("yyyy-MM-dd")
        end_date = self.date_end.date().toString("yyyy-MM-dd")
        
        hasil = ambil_laporan_filter(start_date, end_date)
        
        self.table.setRowCount(0)
        total_omset = 0
        
        for row, (tanggal, nama, jumlah, harga, diskon, subtotal) in enumerate(hasil):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(tanggal))
            self.table.setItem(row, 1, QTableWidgetItem(nama))
            self.table.setItem(row, 2, QTableWidgetItem(str(jumlah)))
            self.table.setItem(row, 3, QTableWidgetItem(f"Rp {int(harga):,}"))
            
            val_diskon = int(diskon) if diskon else 0
            self.table.setItem(row, 4, QTableWidgetItem(f"Rp {val_diskon:,}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"Rp {int(subtotal):,}"))
            
            total_omset += subtotal
        
        self.lbl_total_periode.setText(f"Total Omset: Rp {int(total_omset):,}")
    
    def reset_filter(self):
        """Reset date filters to today"""
        self.date_start.setDate(QDate.currentDate())
        self.date_end.setDate(QDate.currentDate())
        self.muat_laporan()
    
    # ========== EXPORT ==========
    
    def export_csv(self):
        """Export laporan to CSV"""
        start_date = self.date_start.date().toString("yyyy-MM-dd")
        end_date = self.date_end.date().toString("yyyy-MM-dd")
        hasil = ambil_laporan_filter(start_date, end_date)
        
        if not hasil:
            self.show_warning("Kosong", "Tidak ada data untuk diexport.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Simpan CSV",
            str(self.export_folder / f"laporan_{start_date}_{end_date}.csv"),
            "CSV (*.csv)"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Tanggal", "Nama Produk", "Jumlah", "Harga", "Diskon", "Subtotal"])
                writer.writerows(hasil)
            
            self.show_success("Berhasil", f"Data diexport ke:\n{filename}")
            
        except Exception as e:
            self.show_error("Error", str(e))
    
    def export_pdf(self):
        """Export laporan to PDF"""
        start_date = self.date_start.date().toString("yyyy-MM-dd")
        end_date = self.date_end.date().toString("yyyy-MM-dd")
        hasil = ambil_laporan_filter(start_date, end_date)
        
        if not hasil:
            self.show_warning("Kosong", "Tidak ada data.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Simpan PDF",
            str(self.export_folder / f"laporan_{start_date}_{end_date}.pdf"),
            "PDF (*.pdf)"
        )
        
        if not filename:
            return
        
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import (
                SimpleDocTemplate, Table, TableStyle, 
                Paragraph, Spacer
            )
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
            
            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            story.append(Paragraph(
                f"<b>Laporan Penjualan ({start_date} s/d {end_date})</b>",
                styles['Title']
            ))
            story.append(Spacer(1, 12))
            
            # Table data
            data = [["Tanggal", "Produk", "Qty", "Harga", "Disc", "Subtotal"]]
            total_pdf = 0
            
            for row in hasil:
                disc = int(row[4]) if row[4] else 0
                subtotal = row[5]
                total_pdf += subtotal
                
                data.append([
                    row[0], row[1], str(row[2]),
                    f"{int(row[3]):,}", f"{disc:,}", f"{int(subtotal):,}"
                ])
            
            data.append(["", "", "", "", "TOTAL:", f"Rp {int(total_pdf):,}"])
            
            table = Table(data)
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
            
            self.show_success("Berhasil", f"PDF tersimpan di:\n{filename}")
            
        except Exception as e:
            self.show_error("Error", f"Gagal PDF: {str(e)}")