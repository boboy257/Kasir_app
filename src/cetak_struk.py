from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import datetime
from pathlib import Path
from src.settings import load_settings # [BARU] Import ini

# Path Output
ROOT_DIR = Path(__file__).parent.parent
STRUK_FOLDER = ROOT_DIR / "struk"
STRUK_FOLDER.mkdir(exist_ok=True)

def cetak_struk_pdf(nama_toko_ignored, alamat_toko_ignored, keranjang, total):
    """
    Parameter nama_toko dan alamat_toko diabaikan karena kita
    akan mengambil data terbaru langsung dari settings.json
    """
    
    # [BARU] Ambil data dinamis
    settings = load_settings()
    nama_toko = settings.get("nama_toko", "Toko Tanpa Nama")
    alamat_toko = settings.get("alamat_toko", "")
    telepon = settings.get("telepon", "")
    footer_pesan = settings.get("footer_struk", "Terima Kasih")

    filename = f"struk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = str(STRUK_FOLDER / filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # HEADER
    judul = Paragraph(f"<b>{nama_toko}</b>", styles['Title'])
    story.append(judul)
    
    if alamat_toko:
        alamat = Paragraph(alamat_toko, styles['Normal'])
        story.append(alamat)
    if telepon:
        telp = Paragraph(f"Telp: {telepon}", styles['Normal'])
        story.append(telp)
    
    story.append(Spacer(1, 10))
    tanggal = Paragraph(f"Tanggal: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
    story.append(tanggal)
    story.append(Spacer(1, 20))

    # TABEL
    data_tabel = [["Item", "Qty", "Harga", "Disc", "Subtotal"]]
    
    for nama, harga, jumlah, subtotal in keranjang:
        harga_total_asli = harga * jumlah
        nilai_diskon = harga_total_asli - subtotal
        txt_diskon = f"-{int(nilai_diskon):,}" if nilai_diskon > 0 else "0"
        
        data_tabel.append([
            nama, str(jumlah), f"{int(harga):,}", txt_diskon, f"{int(subtotal):,}"
        ])

    data_tabel.append(["", "", "", "TOTAL:", f"Rp {int(total):,}"])

    table = Table(data_tabel, colWidths=[200, 50, 80, 80, 100])
    table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-2), 1, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), 2, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    # FOOTER DARI SETTING
    footer_lines = footer_pesan.split('\n')
    for line in footer_lines:
        story.append(Paragraph(line, styles['Normal']))

    doc.build(story)
    return filepath