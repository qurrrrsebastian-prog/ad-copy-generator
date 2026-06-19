"""Copy frameworks for Indonesian service business. Author: Avatar Putra Sigit

Holds the original AIDA template engine (preserved) plus PAS, 4U, and
Storytelling generators used by the AI Ad Copy Generator app. Every generator
returns a normalized dict: {"headline", "body", "cta"}.
"""
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
    """Generate AIDA copy from templates with dynamic insertion (original engine)."""
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


# ---------------------------------------------------------------------------
# Phase 2: multi-framework engine (AIDA / PAS / 4U / Storytelling)
# ---------------------------------------------------------------------------

# Tone-specific flavor used to color every framework's wording.
TONE_FLAVOR = {
    "Professional": {
        "adj": "andal", "punct": ".",
        "opener": "Solusi {audience} yang terukur",
        "close": "Dipercaya oleh para profesional",
    },
    "Casual": {
        "adj": "gampang", "punct": "!",
        "opener": "Hai {audience}, ada kabar baik nih",
        "close": "Yuk, gas sekarang",
    },
    "Urgent": {
        "adj": "cepat", "punct": "!",
        "opener": "PENTING untuk {audience}",
        "close": "Jangan tunda lagi — slot terbatas",
    },
    "Friendly": {
        "adj": "ramah", "punct": ".",
        "opener": "Buat kamu, {audience}",
        "close": "Kami siap bantu kapan saja",
    },
    "Luxury": {
        "adj": "premium", "punct": ".",
        "opener": "Eksklusif untuk {audience}",
        "close": "Sebuah standar baru kemewahan",
    },
}

# Human-readable label for the audience segment.
AUDIENCE_LABEL = {
    "B2B": "pelaku bisnis", "B2C": "pelanggan", "F&B": "pebisnis kuliner",
    "Property": "pemilik properti", "Tech": "tim teknologi",
    "Health": "penyedia layanan kesehatan", "Fashion": "brand fashion",
}


def _flavor(tone: str) -> dict:
    return TONE_FLAVOR.get(tone, TONE_FLAVOR["Professional"])


def _audience_label(audience: str) -> str:
    return AUDIENCE_LABEL.get(audience, "pelanggan")


def generate_aida_copy(product: str, audience: str, pain_point: str, tone: str, cta: str) -> dict:
    """AIDA → normalized {headline, body, cta} for the new UI."""
    f = _flavor(tone)
    aud = _audience_label(audience)
    headline = f"{product}: {f['opener'].format(audience=aud)}{f['punct']}"
    body = (
        f"Attention — {pain_point.strip().rstrip('.')}.\n"
        f"Interest — {product} hadir dengan pendekatan {f['adj']} yang dirancang untuk {aud}.\n"
        f"Desire — Bayangkan hasil nyata: lebih efisien, lebih tenang, lebih untung.\n"
        f"Action — {f['close']}."
    )
    return {"headline": headline, "body": body, "cta": cta}


def generate_pas_copy(product: str, audience: str, pain_point: str, tone: str, cta: str) -> dict:
    """PAS (Problem-Agitate-Solution)."""
    f = _flavor(tone)
    aud = _audience_label(audience)
    headline = f"Masih terganggu masalah ini, {aud}?{f['punct']}"
    body = (
        f"Problem — {pain_point.strip().rstrip('.')}.\n"
        f"Agitate — Dibiarkan, masalah ini menggerus waktu, biaya, dan reputasi Anda.\n"
        f"Solution — {product} menawarkan solusi {f['adj']} yang langsung menyelesaikannya. {f['close']}."
    )
    return {"headline": headline, "body": body, "cta": cta}


def generate_4u_copy(product: str, audience: str, pain_point: str, tone: str, cta: str) -> dict:
    """4U (Useful, Urgent, Unique, Ultra-specific)."""
    f = _flavor(tone)
    aud = _audience_label(audience)
    headline = f"{product} — {f['adj'].capitalize()}, terbukti untuk {aud}{f['punct']}"
    body = (
        f"Useful — Menjawab langsung: {pain_point.strip().rstrip('.')}.\n"
        f"Urgent — Setiap hari menunda berarti kehilangan peluang.\n"
        f"Unique — Hanya {product} yang menggabungkan kualitas {f['adj']} dengan harga masuk akal.\n"
        f"Ultra-specific — Hasil terukur dalam 30 hari pertama. {f['close']}."
    )
    return {"headline": headline, "body": body, "cta": cta}


def generate_storytelling_copy(product: str, audience: str, pain_point: str, tone: str, cta: str) -> dict:
    """Storytelling (hero's journey, micro)."""
    f = _flavor(tone)
    aud = _audience_label(audience)
    headline = f"Kisah {aud} yang akhirnya menemukan jalan keluar{f['punct']}"
    body = (
        f"Dulu, seperti banyak {aud} lain, mereka berhadapan dengan {pain_point.strip().rstrip('.')}.\n"
        f"Setiap upaya terasa buntu — sampai mereka menemukan {product}.\n"
        f"Dengan pendekatan {f['adj']}, semuanya berubah: beban berkurang, hasil meningkat.\n"
        f"Kini giliran Anda menulis akhir cerita yang sama. {f['close']}."
    )
    return {"headline": headline, "body": body, "cta": cta}


FRAMEWORK_GENERATORS = {
    "AIDA": generate_aida_copy,
    "PAS": generate_pas_copy,
    "4U": generate_4u_copy,
    "Storytelling": generate_storytelling_copy,
}


def generate(product: str, audience: str, pain_point: str, framework: str, tone: str, cta: str) -> dict:
    """Unified entry point. Returns {headline, body, cta}. Falls back to AIDA."""
    gen = FRAMEWORK_GENERATORS.get(framework, generate_aida_copy)
    return gen(product, audience, pain_point, tone, cta)
