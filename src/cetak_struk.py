from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
from pathlib import Path

# Dapatkan path absolut ke folder 'struk'
ROOT_DIR = Path(__file__).parent.parent  # Naik 2 level dari src/
STRUK_FOLDER = ROOT_DIR / "struk"
STRUK_FOLDER.mkdir(exist_ok=True)

def cetak_struk_pdf(nama_toko, alamat_toko, keranjang, total):
    filename = f"struk_pembelian_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = str(STRUK_FOLDER / filename)  # ← Diubah jadi string

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    judul = Paragraph(f"<b>{nama_toko}</b>", styles['Title'])
    story.append(judul)

    if alamat_toko:
        alamat = Paragraph(alamat_toko, styles['Normal'])
        story.append(alamat)
        story.append(Spacer(1, 12))

    tanggal = Paragraph(f"Tanggal: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
    story.append(tanggal)
    story.append(Spacer(1, 12))

    for nama, harga, jumlah, subtotal in keranjang:
        item = Paragraph(f"{nama} x{jumlah} @Rp {harga} = Rp {subtotal}", styles['Normal'])
        story.append(item)

    story.append(Spacer(1, 12))

    total_text = Paragraph(f"<b>Total: Rp {total}</b>", styles['Heading2'])
    story.append(total_text)

    doc.build(story)
    return filepath  # Kembalikan string path