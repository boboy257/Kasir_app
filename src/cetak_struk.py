from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import datetime
from pathlib import Path

# Dapatkan path absolut ke folder 'struk'
ROOT_DIR = Path(__file__).parent.parent
STRUK_FOLDER = ROOT_DIR / "struk"
STRUK_FOLDER.mkdir(exist_ok=True)

def cetak_struk_pdf(nama_toko, alamat_toko, keranjang, total):
    filename = f"struk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = str(STRUK_FOLDER / filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Header
    judul = Paragraph(f"<b>{nama_toko}</b>", styles['Title'])
    story.append(judul)
    if alamat_toko:
        alamat = Paragraph(alamat_toko, styles['Normal'])
        story.append(alamat)
    
    story.append(Spacer(1, 10))
    tanggal = Paragraph(f"Tanggal: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
    story.append(tanggal)
    story.append(Spacer(1, 20))

    # Header Tabel Struk (Ada Kolom Disc)
    data_tabel = [["Item", "Qty", "Harga", "Disc", "Subtotal"]]
    
    # Isi Tabel
    for nama, harga, jumlah, subtotal in keranjang:
        # Hitung diskon manual: (Harga x Qty) - Subtotal yg dibayar
        harga_total_asli = harga * jumlah
        nilai_diskon = harga_total_asli - subtotal
        
        txt_diskon = f"-{int(nilai_diskon):,}" if nilai_diskon > 0 else "0"
        
        data_tabel.append([
            nama,
            str(jumlah),
            f"{int(harga):,}",
            txt_diskon,
            f"{int(subtotal):,}"
        ])

    # Footer Total
    data_tabel.append(["", "", "", "TOTAL:", f"Rp {int(total):,}"])

    # Styling
    tabel = Table(data_tabel, colWidths=[200, 50, 80, 80, 100])
    tabel.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-2), 1, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), 2, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
    ]))
    
    story.append(tabel)
    story.append(Spacer(1, 20))
    story.append(Paragraph("Terima Kasih!", styles['Normal']))

    doc.build(story)
    return filepath