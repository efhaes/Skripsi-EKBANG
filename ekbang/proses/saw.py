from django.db import transaction

from ekbang.models import (
    Warga,
    HasilSAW,
    NormalisasiSAW,
    NormalisasiSAWDetail,
    Kriteria,
    penilaianwarga,
)


def norm_benefit(x, max_val):
    return x / max_val if max_val else 0


def norm_cost(x, min_val):
    return min_val / x if x else 0


@transaction.atomic
def hitung_saw(desa, tahap, tahun):
    warga_list = list(
        Warga.objects.filter(
            desa=desa,
            is_deleted=False
        )
    )

    if not warga_list:
        return

    kriteria_list = list(
        Kriteria.objects.filter(
            desa=desa,
            aktif=True
        )
    )

    if not kriteria_list:
        return

    warga_ids = [w.id for w in warga_list]
    kriteria_ids = [k.id for k in kriteria_list]

    nilai_qs = (
        penilaianwarga.objects
        .filter(
            warga_id__in=warga_ids,
            kriteria_id__in=kriteria_ids
        )
        .select_related("subkriteria")
    )

    nilai_map = {}

    for nk in nilai_qs:
        nilai_map.setdefault(
            nk.warga_id,
            {}
        )[nk.kriteria_id] = nk.subkriteria.nilai

    max_val = {}
    min_val = {}

    for k in kriteria_list:

        nilai_kriteria = [
            nilai_map[w.id][k.id]
            for w in warga_list
            if w.id in nilai_map and k.id in nilai_map[w.id]
        ]

        max_val[k.id] = max(nilai_kriteria) if nilai_kriteria else 0
        min_val[k.id] = min(nilai_kriteria) if nilai_kriteria else 0

    hasil = []

    for w in warga_list:

        detail_records = []
        nilai_total = 0

        for k in kriteria_list:

            nilai_mentah = nilai_map.get(w.id, {}).get(k.id)

            if nilai_mentah is None:
                nilai_normal = 0

            elif k.tipe == "benefit":
                nilai_normal = norm_benefit(
                    nilai_mentah,
                    max_val[k.id]
                )

            else:
                nilai_normal = norm_cost(
                    nilai_mentah,
                    min_val[k.id]
                )

            detail_records.append({
                "kriteria": k,
                "nilai_normalisasi": nilai_normal,
            })

            nilai_total += nilai_normal * k.bobot

        normalisasi, created = NormalisasiSAW.objects.update_or_create(
            desa=desa,
            warga=w,
            tahap=tahap,
            tahun=tahun,
            defaults={
                "is_active": True,
                "nama_warga_arsip": w.nama,
            }
        )

        NormalisasiSAWDetail.objects.filter(
            normalisasi=normalisasi
        ).delete()

        NormalisasiSAWDetail.objects.bulk_create([
            NormalisasiSAWDetail(
                normalisasi=normalisasi,
                kriteria=d["kriteria"],
                nilai_normalisasi=d["nilai_normalisasi"],
            )
            for d in detail_records
        ])

        hasil.append({
            "normalisasi": normalisasi,
            "nilai": nilai_total,
        })

    hasil.sort(
        key=lambda x: x["nilai"],
        reverse=True
    )

    for ranking, h in enumerate(hasil, start=1):

        HasilSAW.objects.update_or_create(
            normalisasi=h["normalisasi"],
            defaults={
                "nilai_preferensi": h["nilai"],
                "ranking": ranking,
            }
        )