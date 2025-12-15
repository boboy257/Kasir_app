from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QFileDialog, QHeaderView,
    QLabel, QDateEdit, QFrame, QAbstractItemView
)
from PyQt6.QtCore import Qt, QDate, QEvent
import csv
from datetime import datetime
from pathlib import Path
from src.database import create_connection, ambil_laporan_filter

class LaporanWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Laporan Penjualan")
        self.setGeometry(100, 100, 1100, 700)

        # --- 1. STYLING DARK MODE ---
        self.setStyleSheet("""
            QWidget { 
                background-color: #121212; 
                color: #e0e0e0; 
                font-family: 'Segoe UI', sans-serif; 
                font-size: 13px;
                outline: none;
            }
            
            /* Input Tanggal */
            QDateEdit { 
                background-color: #1E1E1E; border: 1px solid #555; 
                padding: 8px; color: white; border-radius: 4px; min-width: 110px;
            }
            QDateEdit:focus { border: 2px solid #00E5FF; background-color: #263238; }
            
            /* Tabel */
            QTableWidget { 
                background-color: #1E1E1E; gridline-color: #333; 
                border: 1px solid #333; border-radius: 5px;
            }
            QTableWidget:focus { border: 2px solid #00E5FF; }
            
            QHeaderView::section { 
                background-color: #252525; color: white; 
                padding: 8px; border: none; font-weight: bold; 
            }
            QTableWidget::item:selected { background-color: #00E5FF; color: #000000; }

            /* Tombol Default */
            QPushButton { 
                background-color: #1E1E1E; border: 1px solid #555; 
                padding: 8px 15px; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #333; }
            
            /* FOKUS DEFAULT (Putih) */
            QPushButton:focus { border: 1px solid #ffffff; background-color: #424242; }
            
            QLabel { font-weight: bold; color: #bbb; }
        """)

        self.export_folder = Path("export")
        self.export_folder.mkdir(exist_ok=True)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- 2. HEADER & FILTER AREA ---
        filter_frame = QFrame()
        filter_frame.setStyleSheet("background-color: #181818; border-radius: 8px; border: 1px solid #333;")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(15, 15, 15, 15)
        filter_layout.setSpacing(10)

        # Input Tanggal
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDisplayFormat("yyyy-MM-dd")
        self.date_start.setDate(QDate.currentDate())
        self.date_start.installEventFilter(self)

        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDisplayFormat("yyyy-MM-dd")
        self.date_end.setDate(QDate.currentDate())
        self.date_end.installEventFilter(self)

        # Tombol Filter (Biru)
        self.btn_filter = QPushButton("Terapkan Filter")
        self.btn_filter.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_filter.setStyleSheet("""
            QPushButton { background-color: #2196F3; color: white; border: none; }
            QPushButton:hover { background-color: #1976D2; }
            QPushButton:focus { border: 2px solid #fff; }
        """)
        self.btn_filter.clicked.connect(self.muat_laporan)
        self.btn_filter.installEventFilter(self)

        # Tombol Reset (Focus Orange biar Jelas)
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.setStyleSheet("""
            QPushButton:focus { border: 2px solid #FF9800; color: #FF9800; } /* Fokus Orange */
        """)
        self.btn_reset.clicked.connect(self.reset_filter)
        self.btn_reset.installEventFilter(self)

        filter_layout.addWidget(QLabel("Dari:"))
        filter_layout.addWidget(self.date_start)
        filter_layout.addWidget(QLabel("Sampai:"))
        filter_layout.addWidget(self.date_end)
        filter_layout.addWidget(self.btn_filter)
        filter_layout.addWidget(self.btn_reset)
        filter_layout.addStretch()

        # Tombol Export (Kanan)
        self.btn_csv = QPushButton("Export CSV")
        self.btn_csv.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_csv.setStyleSheet("""
            QPushButton:focus { border: 2px solid #00E676; color: #00E676; } /* Fokus Hijau */
        """)
        self.btn_csv.clicked.connect(self.export_csv)
        self.btn_csv.installEventFilter(self)
        
        self.btn_pdf = QPushButton("Export PDF")
        self.btn_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pdf.setStyleSheet("""
            QPushButton:focus { border: 2px solid #FF5252; color: #FF5252; } /* Fokus Merah */
        """)
        self.btn_pdf.clicked.connect(self.export_pdf)
        self.btn_pdf.installEventFilter(self)
        
        filter_layout.addWidget(self.btn_csv)
        filter_layout.addWidget(self.btn_pdf)

        layout.addWidget(filter_frame)

        # --- 3. TABEL LAPORAN ---
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Tanggal", "Nama Produk", "Jumlah", "Harga", "Disc", "Subtotal"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget { alternate-background-color: #252525; }")
        self.table.installEventFilter(self)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 150); self.table.setColumnWidth(2, 60)
        self.table.setColumnWidth(3, 100); self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 120)
        
        layout.addWidget(self.table)

        # --- 4. FOOTER ---
        footer_layout = QHBoxLayout()
        self.lbl_total_periode = QLabel("Total Omset Periode Ini: Rp 0")
        self.lbl_total_periode.setStyleSheet("font-size: 18px; color: #00E5FF; font-weight: bold;")
        footer_layout.addStretch()
        footer_layout.addWidget(self.lbl_total_periode)
        layout.addLayout(footer_layout)

        self.muat_laporan()
        self.date_start.setFocus() 

    # --- LOGIKA NAVIGASI KEYBOARD (PERBAIKAN TANGGAL) ---
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            
            if event.key() == Qt.Key.Key_Escape:
                self.close()
                return True

            # 1. DATE START (Hapus Navigasi Kanan/Kiri)
            if obj == self.date_start:
                # Cuma ENTER yang pindah widget
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self.date_end.setFocus()
                    return True
                # Bawah -> Tabel
                elif event.key() == Qt.Key.Key_Down: 
                    self.focus_table()
                    return True
                # Kanan/Kiri -> Biarkan Default (Geser Tahun-Bulan-Hari)
            
            # 2. DATE END (Hapus Navigasi Kanan/Kiri)
            elif obj == self.date_end:
                # Cuma ENTER yang pindah widget
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self.btn_filter.setFocus()
                    return True
                elif event.key() == Qt.Key.Key_Down: 
                    self.focus_table()
                    return True
                # Kanan/Kiri -> Biarkan Default

            # 3. TOMBOL FILTER
            elif obj == self.btn_filter:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.btn_filter.click(); return True
                elif event.key() == Qt.Key.Key_Right: self.btn_reset.setFocus(); return True
                elif event.key() == Qt.Key.Key_Left: self.date_end.setFocus(); return True # Kiri balik ke Tanggal
                elif event.key() == Qt.Key.Key_Down: self.focus_table(); return True

            # 4. TOMBOL RESET (Perbaikan: Kanan ke CSV, Kiri ke Filter)
            elif obj == self.btn_reset:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.btn_reset.click(); return True
                elif event.key() == Qt.Key.Key_Right: self.btn_csv.setFocus(); return True
                elif event.key() == Qt.Key.Key_Left: self.btn_filter.setFocus(); return True
                elif event.key() == Qt.Key.Key_Down: self.focus_table(); return True

            # 5. TOMBOL CSV
            elif obj == self.btn_csv:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.btn_csv.click(); return True
                elif event.key() == Qt.Key.Key_Right: self.btn_pdf.setFocus(); return True
                elif event.key() == Qt.Key.Key_Left: self.btn_reset.setFocus(); return True
                elif event.key() == Qt.Key.Key_Down: self.focus_table(); return True

            # 6. TOMBOL PDF
            elif obj == self.btn_pdf:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.btn_pdf.click(); return True
                elif event.key() == Qt.Key.Key_Left: self.btn_csv.setFocus(); return True
                elif event.key() == Qt.Key.Key_Down: self.focus_table(); return True

            # 7. TABEL
            elif obj == self.table:
                if event.key() == Qt.Key.Key_Up and self.table.currentRow() <= 0:
                    self.btn_filter.setFocus()
                    return True

        return super().eventFilter(obj, event)

    def focus_table(self):
        if self.table.rowCount() > 0:
            self.table.setFocus()
            self.table.selectRow(0)

    def muat_laporan(self):
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
        self.date_start.setDate(QDate.currentDate())
        self.date_end.setDate(QDate.currentDate())
        self.muat_laporan()

    def export_csv(self):
        start_date = self.date_start.date().toString("yyyy-MM-dd")
        end_date = self.date_end.date().toString("yyyy-MM-dd")
        hasil = ambil_laporan_filter(start_date, end_date)

        if not hasil:
            QMessageBox.warning(self, "Kosong", "Tidak ada data untuk diexport.")
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Simpan CSV", str(self.export_folder / f"laporan_{start_date}_{end_date}.csv"), "CSV (*.csv)")
        if not filename: return

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Tanggal", "Nama Produk", "Jumlah", "Harga", "Diskon", "Subtotal"])
                writer.writerows(hasil)
            QMessageBox.information(self, "Berhasil", f"Data diexport ke:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def export_pdf(self):
        start_date = self.date_start.date().toString("yyyy-MM-dd")
        end_date = self.date_end.date().toString("yyyy-MM-dd")
        hasil = ambil_laporan_filter(start_date, end_date)

        if not hasil:
            QMessageBox.warning(self, "Kosong", "Tidak ada data.")
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Simpan PDF", str(self.export_folder / f"laporan_{start_date}_{end_date}.pdf"), "PDF (*.pdf)")
        if not filename: return

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors

            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []

            story.append(Paragraph(f"Laporan Penjualan ({start_date} s/d {end_date})", styles['Title']))
            story.append(Spacer(1, 12))

            data = [["Tanggal", "Produk", "Qty", "Harga", "Disc", "Subtotal"]]
            total_pdf = 0
            for row in hasil:
                disc = int(row[4]) if row[4] else 0
                subtotal = row[5]
                total_pdf += subtotal
                data.append([
                    row[0], row[1], str(row[2]), f"{int(row[3]):,}", f"{disc:,}", f"{int(subtotal):,}"
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
            QMessageBox.information(self, "Berhasil", f"PDF tersimpan di:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal PDF: {str(e)}")

    def set_current_user(self, username):
        self.current_user = username