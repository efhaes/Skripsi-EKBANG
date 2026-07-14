# migrate_kecamatan.py

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skripsiSAW.settings')  # sesuaikan nama project kamu
django.setup()

from ekbang.models import Profile, AdminKecamatan

profiles_kecamatan = Profile.objects.filter(role='kecamatan')
print(f"Ditemukan {profiles_kecamatan.count()} profile kecamatan")

for p in profiles_kecamatan:
    obj, created = AdminKecamatan.objects.get_or_create(
        user=p.user,
        defaults={
            'nama_kecamatan': p.user.username,  # sementara pakai username
            'alamat_kantor': '',
        }
    )
    status = "dibuat" if created else "sudah ada"
    print(f"  [{status}] {p.user.username} → AdminKecamatan")

print("Selesai.")