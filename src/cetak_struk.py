from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.units import cm
from datetime import datetime
from pathlib import Path
from src.settings import load_settings

# Path Output
ROOT_DIR = Path(__file__).parent.parent
STRUK_FOLDER = ROOT_DIR / "struk"
STRUK_FOLDER.mkdir(exist_ok=True)

def cetak_struk_pdf(nama_toko_ignored, alamat_toko_ignored, keranjang, total, no_faktur=None, 
                     uang_diterima=0, kembalian=0, nama_kasir="admin"):
    """
    Cetak struk profesional dengan informasi lengkap.
    
    Args:
        nama_toko_ignored: Ignored (ambil dari settings)
        alamat_toko_ignored: Ignored (ambil dari settings)
        keranjang: List of (nama, harga, jumlah, subtotal)
        total: Total transaksi
        no_faktur: Nomor faktur (optional)
        uang_diterima: Uang yang diterima dari customer
        kembalian: Kembalian
        nama_kasir: Nama kasir yang melayani
    
    Returns:
        str: Path file PDF yang dibuat
    """
    
    # Ambil data dinamis dari settings
    settings = load_settings()
    nama_toko = settings.get("nama_toko", "Toko Tanpa Nama")
    alamat_toko = settings.get("alamat_toko", "")
    telepon = settings.get("telepon", "")
    footer_pesan = settings.get("footer_struk", "Terima Kasih")

    # ✅ BUAT FOLDER PER TANGGAL
    tanggal_hari_ini = datetime.now().strftime("%Y-%m-%d")
    folder_tanggal = STRUK_FOLDER / tanggal_hari_ini
    folder_tanggal.mkdir(exist_ok=True)

    # ✅ NAMA FILE PAKAI NOMOR FAKTUR (OVERWRITE KALAU PRINT ULANG)
    if no_faktur:
        filename = f"struk_{no_faktur}.pdf"
    else:
        # Fallback kalau tidak ada nomor faktur
        filename = f"struk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    filepath = str(folder_tanggal / filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, 
                           topMargin=1*cm, bottomMargin=1*cm,
                           leftMargin=1.5*cm, rightMargin=1.5*cm)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Custom Styles
    style_title = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    style_center = ParagraphStyle(
        'Center',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=10,
        spaceAfter=3
    )
    
    style_right = ParagraphStyle(
        'Right',
        parent=styles['Normal'],
        alignment=TA_RIGHT,
        fontSize=10
    )

    # ========== HEADER ==========
    judul = Paragraph(f"<b>{nama_toko}</b>", style_title)
    story.append(judul)
    
    if alamat_toko:
        alamat = Paragraph(alamat_toko, style_center)
        story.append(alamat)
    
    if telepon:
        telp = Paragraph(f"Telp: {telepon}", style_center)
        story.append(telp)
    
    # Garis pemisah
    story.append(Spacer(1, 8))
    story.append(Table([["=" * 80]], colWidths=[18*cm]))
    story.append(Spacer(1, 8))

    # ========== INFO TRANSAKSI ==========
    info_data = []
    
    if no_faktur:
        info_data.append(["No. Faktur", ":", no_faktur])
    
    tanggal_str = datetime.now().strftime('%d/%m/%Y %H:%M')
    info_data.append(["Tanggal", ":", tanggal_str])
    info_data.append(["Kasir", ":", nama_kasir])
    
    info_table = Table(info_data, colWidths=[3*cm, 0.5*cm, 14.5*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
    ]))
    story.append(info_table)
    
    story.append(Spacer(1, 8))
    story.append(Table([["=" * 80]], colWidths=[18*cm]))
    story.append(Spacer(1, 12))

    # ========== TABEL BARANG ==========
    data_tabel = [["Item", "Qty", "Harga", "Disc", "Subtotal"]]
    
    subtotal_keseluruhan = 0
    total_diskon = 0
    
    for nama, harga, jumlah, subtotal in keranjang:
        # Hitung diskon per item
        harga_total_asli = harga * jumlah
        nilai_diskon = harga_total_asli - subtotal
        total_diskon += nilai_diskon
        
        txt_diskon = f"-{int(nilai_diskon):,}" if nilai_diskon > 0 else "0"
        
        data_tabel.append([
            nama, 
            str(jumlah), 
            f"{int(harga):,}", 
            txt_diskon, 
            f"{int(subtotal):,}"
        ])
        
        subtotal_keseluruhan += subtotal

    table = Table(data_tabel, colWidths=[8*cm, 2*cm, 3*cm, 3*cm, 3*cm])
    table.setStyle(TableStyle([
        # Header
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Body
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 12))

    # ========== TOTAL ==========
    total_data = [
        ["SUBTOTAL", f"Rp {int(subtotal_keseluruhan):,}"],
    ]
    
    if total_diskon > 0:
        total_data.append(["DISKON", f"- Rp {int(total_diskon):,}"])
    
    total_data.append(["TOTAL", f"Rp {int(total):,}"])
    
    total_table = Table(total_data, colWidths=[15*cm, 4*cm])
    total_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 2, colors.black),
    ]))
    
    story.append(total_table)
    story.append(Spacer(1, 12))

    # ========== PEMBAYARAN ==========
    if uang_diterima > 0:
        bayar_data = [
            ["TUNAI", f"Rp {int(uang_diterima):,}"],
            ["KEMBALIAN", f"Rp {int(kembalian):,}"],
        ]
        
        bayar_table = Table(bayar_data, colWidths=[15*cm, 4*cm])
        bayar_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TEXTCOLOR', (0, 1), (1, 1), colors.HexColor('#1b5e20')),
        ]))
        
        story.append(bayar_table)
        story.append(Spacer(1, 12))

    # ========== FOOTER ==========
    story.append(Table([["=" * 80]], colWidths=[18*cm]))
    story.append(Spacer(1, 10))
    
    footer_lines = footer_pesan.split('\n')
    for line in footer_lines:
        story.append(Paragraph(line, style_center))

    # Build PDF
    doc.build(story)
    return filepath