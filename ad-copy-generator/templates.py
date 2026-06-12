"""AIDA copy templates for Indonesian service business. Author: Avatar Putra Sigit"""
import random

AIDA_TEMPLATES = {
    "rope_access": {
        "attention": [
            "Gedung tinggi Anda butuh perawatan? Jangan risaukan keselamatan.",
            "Kaca gedung 20 lantai kotor? Rope access adalah solusi tepat.",
            "Biaya maintenance gedung tinggi membengkak? Ada cara lebih efisien."
        ],
        "interest": [
            "Tim kami bersertifikat internasional dengan pengalaman 500+ proyek gedung tinggi.",
            "Teknologi rope access modern memungkinkan pengerjaan 3x lebih cepat dari scaffolding.",
            "Safety record 99.8% — equipment terbaru dan tim berpengalaman."
        ],
        "desire": [
            "Bayangkan gedung Anda kinclong tanpa gangguan operasional kantor.",
            "Hemat 40% biaya maintenance dengan metode rope access yang efisien.",
            "Tampilan profesional gedung Anda meningkatkan citra perusahaan di mata klien."
        ],
        "action": [
            "Dapatkan penawaran gratis hari ini — survey lokasi tanpa biaya.",
            "Hubungi kami sekarang untuk jadwal pengerjaan minggu depan.",
            "Konsultasi gratis: {phone} — slot terbatas untuk bulan ini."
        ]
    },
    "glass_cleaning": {
        "attention": [
            "Kaca gedung Anda terlihat kusam? First impression penting.",
            "Noda dan debu menempel di kaca? Jangan biarkan mengurangi nilai properti.",
            "Pemandangan dari dalam gedung terhalang kotoran kaca?"
        ],
        "interest": [
            "Pembersihan kaca tanpa streak menggunakan equipment tekanan tinggi.",
            "Chemical khusus yang aman untuk kaca tempered dan coating.",
            "Tim bekerja di luar jam operasional untuk minimalkan gangguan."
        ],
        "desire": [
            "Rasakan kembali kejernihan kaca seperti baru — cahaya masuk optimal.",
            "Kenaikan nilai properti hingga 15% dengan facade yang terawat.",
            "Karyawan lebih produktif dengan pemandangan bersih dan pencahayaan alami."
        ],
        "action": [
            "Booking pembersihan bulanan dengan harga spesial — hemat 25%.",
            "Survey dan quotation gratis dalam 24 jam.",
            "WhatsApp sekarang: {phone} untuk jadwal pembersihan."
        ]
    },
    "maintenance": {
        "attention": [
            "Sistem maintenance gedung Anda masih reaktif? Saatnya jadi proaktif.",
            "Biaya perbaikan darurat 3x lebih mahal dari preventive maintenance.",
            "Jadwal maintenance gedung tidak teratur? Risiko kecelakaan meningkat."
        ],
        "interest": [
            "Program AMC (Annual Maintenance Contract) dengan jadwal terstruktur.",
            "Laporan digital setiap pengerjaan — track record lengkap.",
            "Tim multidisiplin: elektrikal, plumbing, structural, dan facade."
        ],
        "desire": [
            "Hemat 30% biaya tahunan dengan maintenance terjadwal.",
            "Perpanjang umur gedung hingga 20 tahun dengan perawatan berkala.",
            "Sertifikat maintenance untuk kebutuhan asuransi dan legal compliance."
        ],
        "action": [
            "Download proposal AMC khusus untuk gedung Anda.",
            "Jadwal meeting dengan facility manager kami — tanpa biaya.",
            "Telepon {phone} untuk assessment gedung gratis."
        ]
    }
}

def generate_aida(product: str, service: str, benefit: str, tone: str, phone: str = "0812-3456-7890") -> dict:
    """Generate AIDA copy from templates with dynamic insertion."""
    try:
        svc = AIDA_TEMPLATES.get(service, AIDA_TEMPLATES["rope_access"])
        return {
            "attention": random.choice(svc["attention"]).replace("Anda", product),
            "interest": random.choice(svc["interest"]) + f" Benefit utama: {benefit}.",
            "desire": random.choice(svc["desire"]),
            "action": random.choice(svc["action"]).replace("{phone}", phone)
        }
    except Exception as e:
        return {
            "attention": f"[Error generating copy: {e}]",
            "interest": "",
            "desire": "",
            "action": ""
        }
