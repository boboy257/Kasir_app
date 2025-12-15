from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLabel, QHeaderView, QAbstractItemView,
    QSpinBox, QFrame, QMessageBox, QInputDialog, QFileDialog
)
from PyQt6.QtCore import Qt, QEvent
from src.database import create_connection, update_stok_produk
import csv
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

class StokRendahWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Laporan Stok Rendah & Restock")
        self.setGeometry(100, 100, 1000, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.setStyleSheet("""
            QWidget { 
                background-color: #121212; 
                color: #e0e0e0; 
                font-family: 'Segoe UI'; 
                font-size: 13px;
                outline: none;
            }
            
            QSpinBox {
                background-color: #1E1E1E; 
                border: 2px solid #333; /* Border awal 2px */
                padding: 5px; 
                color: white; 
                border-radius: 4px; 
                min-width: 80px;
            }
            QSpinBox:focus { 
                border: 2px solid #00E5FF; /* Warna berubah, tebal tetap 2px */
                background-color: #263238; 
            }

            QTableWidget { 
                background-color: #1E1E1E; 
                gridline-color: #333; 
                border: 1px solid #333; 
                border-radius: 5px;
            }
            QTableWidget:focus { border: 2px solid #00E5FF; }
            
            QHeaderView::section { 
                background-color: #252525; color: white; 
                padding: 8px; border: none; font-weight: bold; 
            }
            QTableWidget::item:selected { background-color: #00E5FF; color: #000000; }

            /* TOMBOL COMPACT TAPI JELAS */
            QPushButton { 
                background-color: #1E1E1E; 
                border: 2px solid #333; /* Border default 2px (gelap) */
                padding: 8px 15px;      /* Padding dikembalikan kecil/compact */
                border-radius: 4px; 
                font-weight: bold;
            }
            QPushButton:hover { background-color: #333; }
            
            /* Saat Fokus: Tebal tetap 2px, tapi warnanya jadi Putih Terang */
            QPushButton:focus { 
                border: 2px solid #ffffff; 
                background-color: #424242; 
            }
            
            QLabel { font-weight: bold; color: #bbb; }
        """)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # --- FILTER AREA ---
        filter_frame = QFrame()
        filter_frame.setStyleSheet("background-color: #181818; border-radius: 8px; border: 1px solid #333;")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(15, 15, 15, 15)
        filter_layout.setSpacing(10)

        self.spin_batas = QSpinBox()
        self.spin_batas.setRange(1, 1000)
        self.spin_batas.setValue(5)
        self.spin_batas.setSuffix(" pcs")
        self.spin_batas.installEventFilter(self)

        self.btn_refresh = QPushButton("Filter")
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.setStyleSheet("""
            QPushButton { background-color: #2196F3; color: white; border: 2px solid #2196F3; }
            QPushButton:hover { background-color: #1976D2; }
            QPushButton:focus { border: 2px solid #fff; } /* Warna berubah, ukuran tetap */
        """)
        self.btn_refresh.clicked.connect(self.muat_stok_rendah)
        self.btn_refresh.installEventFilter(self)

        filter_layout.addWidget(QLabel("Batas Stok:"))
        filter_layout.addWidget(self.spin_batas)
        filter_layout.addWidget(self.btn_refresh)
        filter_layout.addStretch()

        # --- TOMBOL AKSI ---
        self.btn_restock = QPushButton("⚡ Restock (F2)")
        self.btn_restock.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_restock.setStyleSheet("""
            QPushButton { border: 2px solid #4CAF50; color: #4CAF50; }
            QPushButton:focus { border: 2px solid #fff; background-color: #1B5E20; }
        """)
        self.btn_restock.clicked.connect(self.aksi_restock)
        self.btn_restock.installEventFilter(self)

        self.btn_csv = QPushButton("Excel/CSV")
        self.btn_csv.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_csv.setStyleSheet("""
            QPushButton { border: 2px solid #FFC107; color: #FFC107; }
            QPushButton:focus { border: 2px solid #fff; background-color: #3e3003; }
        """)
        self.btn_csv.clicked.connect(self.export_csv)
        self.btn_csv.installEventFilter(self)

        self.btn_pdf = QPushButton("Cetak PDF")
        self.btn_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pdf.setStyleSheet("""
            QPushButton { border: 2px solid #F44336; color: #F44336; }
            QPushButton:focus { border: 2px solid #fff; background-color: #3e1212; }
        """)
        self.btn_pdf.clicked.connect(self.export_pdf)
        self.btn_pdf.installEventFilter(self)

        filter_layout.addWidget(self.btn_restock)
        filter_layout.addWidget(self.btn_csv)
        filter_layout.addWidget(self.btn_pdf)

        layout.addWidget(filter_frame)

        # --- TABEL ---
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Barcode", "Nama Produk", "Sisa Stok"])
        self.table.setColumnHidden(0, True) 
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget { alternate-background-color: #252525; }")
        self.table.installEventFilter(self)
        self.table.doubleClicked.connect(self.aksi_restock)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.table)
        layout.addWidget(QLabel("Navigasi: Panah & Enter | F2: Restock | ESC: Tutup", styleSheet="color: #777; font-size: 11px; font-style: italic;"))

        self.muat_stok_rendah()
        self.installEventFilter(self)
        self.spin_batas.setFocus()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape: self.close(); return True
            if event.key() == Qt.Key.Key_F2: self.aksi_restock(); return True

            if obj == self.spin_batas:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.muat_stok_rendah(); return True
                elif event.key() == Qt.Key.Key_Right: self.btn_refresh.setFocus(); return True
                elif event.key() == Qt.Key.Key_Down: self.table.setFocus(); return True

            elif obj == self.btn_refresh:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.btn_refresh.click(); return True
                elif event.key() == Qt.Key.Key_Right: self.btn_restock.setFocus(); return True
                elif event.key() == Qt.Key.Key_Left: self.spin_batas.setFocus(); return True
                elif event.key() == Qt.Key.Key_Down: self.table.setFocus(); return True

            elif obj == self.btn_restock:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.btn_restock.click(); return True
                elif event.key() == Qt.Key.Key_Right: self.btn_csv.setFocus(); return True
                elif event.key() == Qt.Key.Key_Left: self.btn_refresh.setFocus(); return True
                elif event.key() == Qt.Key.Key_Down: self.table.setFocus(); return True

            elif obj == self.btn_csv:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.btn_csv.click(); return True
                elif event.key() == Qt.Key.Key_Right: self.btn_pdf.setFocus(); return True
                elif event.key() == Qt.Key.Key_Left: self.btn_restock.setFocus(); return True
                elif event.key() == Qt.Key.Key_Down: self.table.setFocus(); return True

            elif obj == self.btn_pdf:
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.btn_pdf.click(); return True
                elif event.key() == Qt.Key.Key_Left: self.btn_csv.setFocus(); return True
                elif event.key() == Qt.Key.Key_Down: self.table.setFocus(); return True

            elif obj == self.table:
                if event.key() == Qt.Key.Key_Up and self.table.currentRow() <= 0: self.spin_batas.setFocus(); return True
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter): self.aksi_restock(); return True

        return super().eventFilter(obj, event)

    def muat_stok_rendah(self):
        self.table.setRowCount(0)
        batas = self.spin_batas.value()
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, barcode, nama, stok FROM produk WHERE stok < ? ORDER BY stok ASC", (batas,))
        hasil = cursor.fetchall()
        conn.close()
        for row, (id_produk, barcode, nama, stok) in enumerate(hasil):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(id_produk)))
            self.table.setItem(row, 1, QTableWidgetItem(barcode))
            self.table.setItem(row, 2, QTableWidgetItem(nama))
            item_stok = QTableWidgetItem(str(stok))
            item_stok.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if stok <= 0:
                item_stok.setForeground(Qt.GlobalColor.red); item_stok.setText("HABIS (0)")
            else:
                item_stok.setForeground(Qt.GlobalColor.yellow)
            self.table.setItem(row, 3, item_stok)

    def aksi_restock(self):
        row = self.table.currentRow()
        if row < 0: QMessageBox.warning(self, "Pilih Produk", "Pilih produk yang ingin direstock."); return
        id_produk = self.table.item(row, 0).text()
        nama = self.table.item(row, 2).text()
        stok_text = self.table.item(row, 3).text()
        stok_lama = 0 if "(" in stok_text else int(stok_text)
        jumlah, ok = QInputDialog.getInt(self, "Restock Cepat", f"Tambah stok '{nama}':\n(Sisa: {stok_lama})", min=1, max=1000)
        if ok:
            update_stok_produk(id_produk, stok_lama + jumlah)
            self.muat_stok_rendah()
            QMessageBox.information(self, "Sukses", f"Stok '{nama}' bertambah.")

    def export_csv(self):
        if self.table.rowCount() == 0: return
        filename, _ = QFileDialog.getSaveFileName(self, "Simpan CSV", "daftar_belanja.csv", "CSV (*.csv)")
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Barcode", "Nama Produk", "Sisa Stok", "Beli"])
                    for row in range(self.table.rowCount()):
                        writer.writerow([self.table.item(row, 1).text(), self.table.item(row, 2).text(), self.table.item(row, 3).text(), ""])
                QMessageBox.information(self, "Berhasil", "File CSV tersimpan.")
            except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def export_pdf(self):
        if self.table.rowCount() == 0: return
        filename, _ = QFileDialog.getSaveFileName(self, "Simpan PDF", "daftar_belanja.pdf", "PDF (*.pdf)")
        if not filename: return
        try:
            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            tgl = datetime.now().strftime('%Y-%m-%d %H:%M')
            story.append(Paragraph(f"<b>DAFTAR BELANJA / KULAKAN</b>", styles['Title']))
            story.append(Paragraph(f"Dicetak: {tgl}", styles['Normal']))
            story.append(Spacer(1, 12))
            data = [["No", "Barcode", "Nama Produk", "Sisa", "Ceklis"]]
            for row in range(self.table.rowCount()):
                data.append([str(row+1), self.table.item(row, 1).text(), self.table.item(row, 2).text(), self.table.item(row, 3).text(), "[   ]"])
            table = Table(data, colWidths=[30, 80, 200, 60, 80])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            story.append(table)
            doc.build(story)
            QMessageBox.information(self, "Berhasil", "PDF tersimpan.")
            import os, platform
            if platform.system() == 'Windows': os.startfile(filename)
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def set_current_user(self, username):
        self.current_user = username