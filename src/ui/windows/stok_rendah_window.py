from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel, 
    QSpinBox, QFrame, QInputDialog, QFileDialog
)
from PyQt6.QtCore import Qt
from datetime import datetime
import csv

from src.ui.base.base_window import BaseWindow
from src.ui.base.style_manager import StyleManager
from src.ui.widgets.smart_table import SmartTable
from src.database import create_connection, update_stok_produk


class StokRendahWindow(BaseWindow):
    
    def __init__(self):
        super().__init__()
        
        self.setup_ui()
        self.setup_navigation()
        self.muat_stok_rendah()
        
        self.setWindowTitle("Laporan Stok Rendah & Restock")
        self.setGeometry(100, 100, 1000, 600)
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        filter_frame = QFrame()
        filter_frame.setStyleSheet(
            "background-color: #181818; border-radius: 8px; border: 1px solid #333;"
        )
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(15, 15, 15, 15)
        filter_layout.setSpacing(10)
        
        self.spin_batas = QSpinBox()
        self.spin_batas.setRange(1, 1000)
        self.spin_batas.setValue(5)
        self.spin_batas.setSuffix(" pcs")
        
        style = StyleManager()
        
        self.btn_refresh = QPushButton("Filter")
        self.btn_refresh.setStyleSheet(style.get_button_style('primary'))
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.muat_stok_rendah)
        
        filter_layout.addWidget(QLabel("Batas Stok:"))
        filter_layout.addWidget(self.spin_batas)
        filter_layout.addWidget(self.btn_refresh)
        filter_layout.addStretch()
        
        self.btn_restock = QPushButton("⚡ Restock (F2)")
        self.btn_restock.setStyleSheet(style.get_button_style('success'))
        self.btn_restock.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_restock.clicked.connect(self.aksi_restock)
        
        self.btn_csv = QPushButton("Excel/CSV")
        self.btn_csv.setStyleSheet(style.get_button_style('default'))
        self.btn_csv.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_csv.clicked.connect(self.export_csv)
        
        self.btn_pdf = QPushButton("Cetak PDF")
        self.btn_pdf.setStyleSheet(style.get_button_style('default'))
        self.btn_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pdf.clicked.connect(self.export_pdf)
        
        filter_layout.addWidget(self.btn_restock)
        filter_layout.addWidget(self.btn_csv)
        filter_layout.addWidget(self.btn_pdf)
        
        layout.addWidget(filter_frame)
        
        self.table = SmartTable(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Barcode", "Nama Produk", "Sisa Stok"])
        self.table.setColumnHidden(0, True)
        self.table.stretch_column(2)
        
        layout.addWidget(self.table)
        
        layout.addWidget(QLabel(
            "F2=Restock | ESC=Close",
            styleSheet="color: #777; font-size: 11px; font-style: italic;"
        ))
        
        self.spin_batas.setFocus()
    
    def setup_navigation(self):
        self.register_navigation(self.spin_batas, {
            Qt.Key.Key_Return: self.muat_stok_rendah,
            Qt.Key.Key_Right: self.btn_refresh
        })
        
        self.register_navigation(self.btn_refresh, {
            Qt.Key.Key_Return: self.muat_stok_rendah,
            Qt.Key.Key_Right: self.btn_restock,
            Qt.Key.Key_Left: self.spin_batas
        })
        
        self.register_navigation(self.btn_restock, {
            Qt.Key.Key_Return: self.aksi_restock,
            Qt.Key.Key_Right: self.btn_csv,
            Qt.Key.Key_Left: self.btn_refresh
        })
        
        self.register_navigation(self.btn_csv, {
            Qt.Key.Key_Return: self.export_csv,
            Qt.Key.Key_Right: self.btn_pdf,
            Qt.Key.Key_Left: self.btn_restock
        })
        
        self.register_navigation(self.btn_pdf, {
            Qt.Key.Key_Return: self.export_pdf,
            Qt.Key.Key_Left: self.btn_csv
        })
        
        self.register_table_callbacks(self.table, {
            'edit': self.aksi_restock,
            'focus_up': self.spin_batas
        })
        
        self.register_shortcut(Qt.Key.Key_F2, self.aksi_restock)
    
    def muat_stok_rendah(self):
        self.table.clear_table()
        batas = self.spin_batas.value()
        
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, barcode, nama, stok FROM produk WHERE stok < ? ORDER BY stok ASC",
            (batas,)
        )
        hasil = cursor.fetchall()
        conn.close()
        
        from PyQt6.QtWidgets import QTableWidgetItem
        
        for row, (id_produk, barcode, nama, stok) in enumerate(hasil):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(id_produk)))
            self.table.setItem(row, 1, QTableWidgetItem(barcode))
            self.table.setItem(row, 2, QTableWidgetItem(nama))
            
            item_stok = QTableWidgetItem(str(stok))
            item_stok.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if stok <= 0:
                item_stok.setForeground(Qt.GlobalColor.red)
                item_stok.setText("HABIS (0)")
            else:
                item_stok.setForeground(Qt.GlobalColor.yellow)
            
            self.table.setItem(row, 3, item_stok)
    
    def aksi_restock(self):
        row = self.table.currentRow()
        if row < 0:
            self.show_warning("Pilih Produk", "Pilih produk yang ingin direstock.")
            return
        
        id_produk = self.table.item(row, 0).text()
        nama = self.table.item(row, 2).text()
        stok_text = self.table.item(row, 3).text()
        stok_lama = 0 if "(" in stok_text else int(stok_text)
        
        jumlah, ok = QInputDialog.getInt(
            self, "Restock Cepat",
            f"Tambah stok '{nama}':\n(Sisa: {stok_lama})",
            min=1, max=1000
        )
        
        if ok:
            update_stok_produk(id_produk, stok_lama + jumlah)
            self.muat_stok_rendah()
            self.show_success("Sukses", f"Stok '{nama}' bertambah.")
    
    def export_csv(self):
        if self.table.rowCount() == 0:
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Simpan CSV", "daftar_belanja.csv", "CSV (*.csv)"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Barcode", "Nama Produk", "Sisa Stok", "Beli"])
                    
                    for row in range(self.table.rowCount()):
                        writer.writerow([
                            self.table.item(row, 1).text(),
                            self.table.item(row, 2).text(),
                            self.table.item(row, 3).text(),
                            ""
                        ])
                
                self.show_success("Berhasil", "File CSV tersimpan.")
            except Exception as e:
                self.show_error("Error", str(e))
    
    def export_pdf(self):
        if self.table.rowCount() == 0:
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Simpan PDF", "daftar_belanja.pdf", "PDF (*.pdf)"
        )
        
        if not filename:
            return
        
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
            from reportlab.lib import colors
            
            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []
            
            data = [["No", "Barcode", "Nama Produk", "Sisa", "Ceklis"]]
            for row in range(self.table.rowCount()):
                data.append([
                    str(row + 1),
                    self.table.item(row, 1).text(),
                    self.table.item(row, 2).text(),
                    self.table.item(row, 3).text(),
                    "[   ]"
                ])
            
            table = Table(data, colWidths=[30, 80, 200, 60, 80])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            
            story.append(table)
            doc.build(story)
            
            self.show_success("Berhasil", "PDF tersimpan.")
            
            import os, platform
            if platform.system() == 'Windows':
                os.startfile(filename)
                
        except Exception as e:
            self.show_error("Error", str(e))