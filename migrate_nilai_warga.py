# exec(open('validasi_final.py', encoding='utf-8').read())

from ekbang.models import Warga, WargaNilaiKriteria

KRITERIA_LAMA = ['desil_p3ke', 'kehilangan_pekerjaan', 'sakit_kronis', 'lansia_tunggal', 'perempuan_kepala']

cocok = 0
tidak_cocok = 0

for warga in Warga.objects.all():
    for kode in KRITERIA_LAMA:
        value_lama = getattr(warga, kode)
        nk = WargaNilaiKriteria.objects.filter(warga=warga, kriteria__kode=kode).first()

        if nk is None:
            print(f"❌ {warga.nama} - {kode}: TIDAK ADA WargaNilaiKriteria")
            tidak_cocok += 1
            continue

        nilai_baru = int(nk.subkriteria.nilai)
        if nilai_baru != value_lama:
            print(f"❌ {warga.nama} - {kode}: lama={value_lama} vs baru={nilai_baru}")
            tidak_cocok += 1
        else:
            cocok += 1

print("\n" + "=" * 60)
print(f"✅ Cocok: {cocok}")
print(f"❌ Tidak cocok: {tidak_cocok}")

if tidak_cocok == 0:
    print("\n🎉 SEMUA DATA COCOK. Aman lanjut hapus field lama.")
else:
    print("\n⚠️  JANGAN hapus field lama dulu, ada data yang nggak cocok!")