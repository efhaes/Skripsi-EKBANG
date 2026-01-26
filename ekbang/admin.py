from django.contrib import admin
from .models import (
    Profile,
    Desa,
    Warga,
    HasilSAW,
    PengajuanBLT,
    NormalisasiSAW
)

# =========================
# PROFILE
# =========================
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username',)


# =========================
# DESA
# =========================
@admin.register(Desa)
class DesaAdmin(admin.ModelAdmin):
    list_display = (
        'nama_desa',
        'kecamatan',
        'user',
        'dibuat_oleh',
        'created_at'
    )
    list_filter = ('kecamatan',)
    search_fields = ('nama_desa', 'user__username')
    readonly_fields = ('created_at',)


# =========================
# WARGA
# =========================
@admin.register(Warga)
class WargaAdmin(admin.ModelAdmin):
    list_display = (
        'nik',
        'nama',
        'desa',
        'desil_p3ke',
        'kehilangan_pekerjaan',
        'sakit_kronis'
    )
    list_filter = ('desa',)
    search_fields = ('nik', 'nama')


# =========================
# HASIL SAW
# =========================
@admin.register(HasilSAW)
class HasilSAWAdmin(admin.ModelAdmin):
    list_display = (
        'warga',
        'desa',
        'nilai_preferensi',
        'ranking',
        'tanggal_proses'
    )
    list_filter = ('desa',)
    ordering = ('ranking',)
    readonly_fields = ('tanggal_proses',)


# =========================
# PENGAJUAN BLT
# =========================
@admin.register(PengajuanBLT)
class PengajuanBLTAdmin(admin.ModelAdmin):
    list_display = (
        'desa',
        'tahun',
        'tahap',
        'jumlah_kpm',
        'jumlah_dana',
        'status',
        'created_at'
    )
    list_filter = ('status', 'tahun', 'tahap')
    search_fields = ('desa__nama_desa',)
    readonly_fields = ('created_at',)




# =========================
# NORMALISASI SAW  🔥
# =========================
@admin.register(NormalisasiSAW)
class NormalisasiSAWAdmin(admin.ModelAdmin):
    list_display = (
        'warga',
        'desa',
        'desil_p3ke',
        'kehilangan_pekerjaan',
        'sakit_kronis',
        'pkh',
        'lansia_tunggal',
        'perempuan_kepala',
        'created_at'
    )

    list_filter = ('desa', 'created_at')
    search_fields = ('warga__nama', 'warga__nik')
    readonly_fields = ('created_at',)