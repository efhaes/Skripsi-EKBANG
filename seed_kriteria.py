# Jalankan di: python manage.py shell < seed_kriteria.py
# Jalankan SETELAH cek_data_warga.py hasilnya bersih.
# Script ini CUMA bikin Kriteria + Subkriteria, belum menyentuh data Warga sama sekali.

from ekbang.models import Desa, Kriteria, Subkriteria
from ekbang.proses.data_saw import SUBKRITERIA

KRITERIA_LAMA = ['desil_p3ke', 'kehilangan_pekerjaan', 'sakit_kronis', 'lansia_tunggal', 'perempuan_kepala']

NAMA_KRITERIA = {
    'desil_p3ke': 'Desil P3KE',
    'kehilangan_pekerjaan': 'Kehilangan Pekerjaan',
    'sakit_kronis': 'Sakit Kronis',
    'lansia_tunggal': 'Lansia Tunggal',
    'perempuan_kepala': 'Perempuan Kepala Keluarga',
}

# Sesuaikan bobot ini kalau lu punya nilai bobot SAW asli yang berbeda
BOBOT_KRITERIA = {
    'desil_p3ke': 0.2,
    'kehilangan_pekerjaan': 0.2,
    'sakit_kronis': 0.2,
    'lansia_tunggal': 0.2,
    'perempuan_kepala': 0.2,
}

total_kriteria = 0
total_subkriteria = 0

for desa in Desa.objects.all():
    print(f"\n📍 Seeding kriteria untuk: {desa.nama_desa}")

    for urutan, kode in enumerate(KRITERIA_LAMA):
        kriteria, created = Kriteria.objects.get_or_create(
            desa=desa,
            kode=kode,
            defaults={
                'nama': NAMA_KRITERIA[kode],
                'bobot': BOBOT_KRITERIA[kode],
                'tipe': 'benefit',
                'urutan': urutan,
                'aktif': True,
            }
        )
        if created:
            total_kriteria += 1
            print(f"  ✅ Kriteria dibuat: {kriteria.nama}")
        else:
            print(f"  ⏭️  Kriteria sudah ada: {kriteria.nama}")

        for value, label in SUBKRITERIA[kode]:
            sub, sub_created = Subkriteria.objects.get_or_create(
                kriteria=kriteria,
                label=str(label),
                defaults={'nilai': float(value), 'urutan': int(value)}
            )
            if sub_created:
                total_subkriteria += 1

print("\n" + "=" * 60)
print(f"✅ Selesai. {total_kriteria} Kriteria baru, {total_subkriteria} Subkriteria baru dibuat.")
print("Cek total bobot per desa harus = 1.0 sebelum lanjut ke tahap pindahin nilai warga.")

for desa in Desa.objects.all():
    total_bobot = sum(k.bobot for k in Kriteria.objects.filter(desa=desa))
    status = "✅" if abs(total_bobot - 1.0) < 0.001 else "⚠️"
    print(f"{status} {desa.nama_desa}: total bobot = {total_bobot}")
    