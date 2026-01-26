from ekbang.models import Warga, HasilSAW,NormalisasiSAW
from django.db import transaction
BOBOT = {
    'desil_p3ke': 0.25,
    'kehilangan_pekerjaan': 0.20,
    'sakit_kronis': 0.20,
    'tidak_pkh': 0.15,
    'lansia_tunggal': 0.10,
    'perempuan_kepala': 0.10,
}

KRITERIA = {
    'desil_p3ke': 'cost',
    'kehilangan_pekerjaan': 'benefit',
    'sakit_kronis': 'benefit',
    'tidak_pkh': 'cost',
    'lansia_tunggal': 'benefit',
    'perempuan_kepala': 'benefit',
}

def norm_benefit(x, max_val):
    return x / max_val if max_val else 0

def norm_cost(x, min_val):
    return min_val / x if x else 0




@transaction.atomic
def hitung_saw(desa):
    warga_list = Warga.objects.filter(desa=desa)

    if not warga_list.exists():
        return

    # =========================
    # 1️⃣ MAX & MIN
    # =========================
    max_val = {
        'desil_p3ke': max(w.desil_p3ke for w in warga_list),
        'kehilangan_pekerjaan': max(w.kehilangan_pekerjaan for w in warga_list),
        'sakit_kronis': max(w.sakit_kronis for w in warga_list),
        'tidak_pkh': max(w.tidak_pkh for w in warga_list),
        'lansia_tunggal': max(w.lansia_tunggal for w in warga_list),
        'perempuan_kepala': max(w.perempuan_kepala for w in warga_list),
    }

    min_val = {
        'desil_p3ke': min(w.desil_p3ke for w in warga_list),
        'tidak_pkh': min(w.tidak_pkh for w in warga_list),
    }

    # =========================
    # 2️⃣ BERSIHKAN DATA LAMA
    # =========================
    HasilSAW.objects.filter(desa=desa).delete()
    NormalisasiSAW.objects.filter(desa=desa).delete()

    hasil = []

    # =========================
    # 3️⃣ HITUNG NORMALISASI
    # =========================
    for w in warga_list:
        norm = {}

        for k in BOBOT:
            if KRITERIA[k] == 'benefit':
                norm[k] = norm_benefit(getattr(w, k), max_val[k])
            else:
                norm[k] = norm_cost(getattr(w, k), min_val[k])

        nilai = sum(norm[k] * BOBOT[k] for k in BOBOT)

        # 🔹 SIMPAN NORMALISASI
        NormalisasiSAW.objects.create(
            desa=desa,
            warga=w,
            desil_p3ke=norm['desil_p3ke'],
            kehilangan_pekerjaan=norm['kehilangan_pekerjaan'],
            sakit_kronis=norm['sakit_kronis'],
            pkh=norm['tidak_pkh'],
            lansia_tunggal=norm['lansia_tunggal'],
            perempuan_kepala=norm['perempuan_kepala'],
        )

        hasil.append({
            'warga': w,
            'nilai': nilai
        })

    # =========================
    # 4️⃣ SORT & SIMPAN RANKING
    # =========================
    hasil.sort(key=lambda x: x['nilai'], reverse=True)

    for i, h in enumerate(hasil, start=1):
        HasilSAW.objects.create(
            desa=desa,
            warga=h['warga'],
            nilai_preferensi=h['nilai'],
            ranking=i
        )


