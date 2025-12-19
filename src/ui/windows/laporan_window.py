"""
Laporan Window - SmartNavigation REFACTORED
============================================
Filter row (circular) + table + action buttons
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel, QDateEdit, QFrame,
    QFileDialog
)
from PyQt6.QtCore import Qt, QDate
import csv
from datetime import datetime

from src.ui.base.base_window import BaseWindow
from src.ui.base.style_manager import StyleManager
from src.ui.widgets.smart_table import SmartTable
from src.database import ambil_laporan_filter
from src.config.paths import EXPORT_FOLDER


class LaporanWindow(BaseWindow):
    """Sales report dengan smart button row navigation"""
    
    def __init__(self):
        super().__init__()
        
        self.export_folder = EXPORT_FOLDER
        self.export_folder.mkdir(parents=True, exist_ok=True)
        
        self.setup_ui()
        self.setup_navigation()
        
        self.setWindowTitle("Laporan Penjualan")
        self.setGeometry(100, 100, 1100, 700)
        
        self.muat_laporan()
    
    def setup_ui(self):
        """Setup UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Filter frame
        filter_frame = QFrame()
        filter_frame.setStyleSheet(
            "background-color: #181818; border-radius: 8px; border: 1px solid #333;"
        )
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(15, 15, 15, 15)
        filter_layout.setSpacing(10)
        
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDisplayFormat("yyyy-MM-dd")
        self.date_start.setDate(QDate.currentDate())
        
        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDisplayFormat("yyyy-MM-dd")
        self.date_end.setDate(QDate.currentDate())
        
        style = StyleManager()
        
        self.btn_filter = QPushButton("Filter")
        self.btn_filter.setStyleSheet(style.get_button_style('primary'))
        self.btn_filter.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_filter.clicked.connect(self.muat_laporan)
        
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setStyleSheet(style.get_button_style('default'))
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self.reset_filter)
        
        self.btn_csv = QPushButton("CSV")
        self.btn_csv.setStyleSheet(style.get_button_style('success'))
        self.btn_csv.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_csv.clicked.connect(self.export_csv)
        
        self.btn_pdf = QPushButton("PDF")
        self.btn_pdf.setStyleSheet(style.get_button_style('danger'))
        self.btn_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pdf.clicked.connect(self.export_pdf)
        
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
        
        # Table
        self.table = SmartTable(0, 6)
        self.table.setHorizontalHeaderLabels([
            "Tanggal", "Nama Produk", "Jumlah", "Harga", "Disc", "Subtotal"
        ])
        self.table.stretch_column(1)
        self.table.set_column_width(0, 150)
        self.table.set_column_width(2, 60)
        self.table.set_column_width(3, 100)
        self.table.set_column_width(4, 80)
        self.table.set_column_width(5, 120)
        
        layout.addWidget(self.table)
        
        # Footer
        footer_layout = QHBoxLayout()
        
        self.lbl_total_periode = QLabel("Total Omset: Rp 0")
        self.lbl_total_periode.setStyleSheet(
            "font-size: 18px; color: #00E5FF; font-weight: bold;"
        )
        
        footer_layout.addStretch()
        footer_layout.addWidget(self.lbl_total_periode)
        layout.addLayout(footer_layout)
        
        self.date_start.setFocus()
    
    def setup_navigation(self):
        """
        SmartNavigation:
        - Filter row: 6 buttons circular
        - Table: Up/Down
        """
        
        # Filter + action buttons as single circular row
        button_row = [
            self.date_start,
            self.date_end,
            self.btn_filter,
            self.btn_reset,
            self.btn_csv,
            self.btn_pdf
        ]
        
        self.register_navigation_row(button_row, circular=True)
        
        # Custom behavior per widget
        # Dates: Enter = Next
        self.register_navigation(self.date_start, {
            Qt.Key.Key_Return: self.date_end,
            Qt.Key.Key_Down: lambda: self.focus_table_first_row(self.table)
        })
        
        self.register_navigation(self.date_end, {
            Qt.Key.Key_Return: self.btn_filter,
            Qt.Key.Key_Down: lambda: self.focus_table_first_row(self.table)
        })
        
        # Buttons: Enter = Click, Down = Table
        for btn in [self.btn_filter, self.btn_reset, self.btn_csv, self.btn_pdf]:
            self.register_navigation(btn, {
                Qt.Key.Key_Return: lambda b=btn: b.click(),
                Qt.Key.Key_Down: lambda: self.focus_table_first_row(self.table)
            })
        
        # Table: Up = Back to filter
        self.register_table_callbacks(self.table, {
            'focus_up': self.date_start
        })
    
    # Data operations
    def muat_laporan(self):
        """Load report data"""
        start_date = self.date_start.date().toString("yyyy-MM-dd")
        end_date = self.date_end.date().toString("yyyy-MM-dd")
        
        hasil = ambil_laporan_filter(start_date, end_date)
        
        self.table.clear_table()
        total_omset = 0
        
        from PyQt6.QtWidgets import QTableWidgetItem
        
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
        """Reset to today"""
        self.date_start.setDate(QDate.currentDate())
        self.date_end.setDate(QDate.currentDate())
        self.muat_laporan()
    
    def export_csv(self):
        """Export to CSV"""
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
        """Export to PDF"""
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
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
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