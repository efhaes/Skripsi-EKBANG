from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    AdminKecamatan,
    Desa,
    Warga,
    Kriteria,
    Subkriteria,
    penilaianwarga,
    KuotaKPM,
    NormalisasiSAW,
    NormalisasiSAWDetail,
    HasilSAW,
    PengajuanBLT,
)


# =========================================================
# USER
# =========================================================

class AdminKecamatanInline(admin.StackedInline):
    model = AdminKecamatan
    can_delete = False
    extra = 0
    verbose_name_plural = "Admin Kecamatan"


class DesaInline(admin.StackedInline):
    model = Desa
    can_delete = False
    extra = 0
    verbose_name_plural = "Desa"


class UserAdmin(BaseUserAdmin):
    inlines = (AdminKecamatanInline, DesaInline)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# =========================================================
# ADMIN KECAMATAN
# =========================================================

@admin.register(AdminKecamatan)
class AdminKecamatanAdmin(admin.ModelAdmin):
    list_display = (
        "nama_kecamatan",
        "user",
        "alamat_kantor",
        "created_at",
    )

    search_fields = (
        "nama_kecamatan",
        "user__username",
    )

    readonly_fields = (
        "created_at",
    )


# =========================================================
# DESA
# =========================================================

@admin.register(Desa)
class DesaAdmin(admin.ModelAdmin):
    list_display = (
        "nama_desa",
        "kecamatan",
        "user",
        "dibuat_oleh",
        "created_at",
    )

    search_fields = (
        "nama_desa",
        "kecamatan",
        "user__username",
    )

    list_filter = (
        "kecamatan",
        "dibuat_oleh",
    )

    readonly_fields = (
        "created_at",
    )


# =========================================================
# KRITERIA
# =========================================================

class SubkriteriaInline(admin.TabularInline):
    model = Subkriteria
    extra = 0


@admin.register(Kriteria)
class KriteriaAdmin(admin.ModelAdmin):
    list_display = (
        "kode",
        "nama",
        "desa",
        "bobot",
        "tipe",
        "urutan",
        "aktif",
    )

    list_filter = (
        "desa",
        "tipe",
        "aktif",
    )

    search_fields = (
        "kode",
        "nama",
    )

    ordering = (
        "desa",
        "urutan",
    )

    inlines = [
        SubkriteriaInline
    ]


# =========================================================
# WARGA
# =========================================================

@admin.register(Warga)
class WargaAdmin(admin.ModelAdmin):
    list_display = (
        "nama",
        "nik",
        "desa",
        "jumlah_keluarga_kpm",
    )

    search_fields = (
        "nama",
        "nik",
    )

    list_filter = (
        "desa",
    )

    fieldsets = (
        (
            "Data Warga",
            {
                "fields": (
                    "desa",
                    "nik",
                    "nama",
                    "jumlah_keluarga_kpm",
                    "alamat",
                )
            },
        ),
    )


# =========================================================
# PENILAIAN WARGA
# =========================================================

@admin.register(penilaianwarga)
class PenilaianWargaAdmin(admin.ModelAdmin):
    list_display = (
        "warga",
        "kriteria",
        "subkriteria",
        "updated_at",
    )

    search_fields = (
        "warga__nama",
        "kriteria__nama",
        "subkriteria__label",
    )

    list_filter = (
        "kriteria",
        "warga__desa",
    )

    readonly_fields = (
        "updated_at",
    )


# =========================================================
# KUOTA KPM
# =========================================================

@admin.register(KuotaKPM)
class KuotaKPMAdmin(admin.ModelAdmin):
    list_display = (
        "desa",
        "tahap",
        "tahun",
        "jumlah",
        "updated_at",
    )

    search_fields = (
        "desa__nama_desa",
    )

    list_filter = (
        "tahun",
        "tahap",
        "desa",
    )

    readonly_fields = (
        "updated_at",
    )


# =========================================================
# NORMALISASI SAW
# =========================================================

class NormalisasiSAWDetailInline(admin.TabularInline):
    model = NormalisasiSAWDetail
    extra = 0


@admin.register(NormalisasiSAW)
class NormalisasiSAWAdmin(admin.ModelAdmin):
    list_display = (
        "warga",
        "desa",
        "tahap",
        "tahun",
        "is_active",
        "created_at",
    )

    search_fields = (
        "warga__nama",
        "desa__nama_desa",
    )

    list_filter = (
        "desa",
        "tahun",
        "tahap",
        "is_active",
    )

    readonly_fields = (
        "created_at",
    )

    inlines = [
        NormalisasiSAWDetailInline,
    ]


# =========================================================
# HASIL SAW
# =========================================================

@admin.register(HasilSAW)
class HasilSAWAdmin(admin.ModelAdmin):

    list_display = (
        "get_warga",
        "get_desa",
        "get_tahap",
        "get_tahun",
        "nilai_preferensi",
        "ranking",
        "tanggal_proses",
    )

    search_fields = (
        "normalisasi__warga__nama",
        "normalisasi__desa__nama_desa",
    )

    list_filter = (
        "normalisasi__desa",
        "normalisasi__tahun",
        "normalisasi__tahap",
    )

    readonly_fields = (
        "tanggal_proses",
    )

    @admin.display(description="Warga")
    def get_warga(self, obj):
        return obj.normalisasi.warga

    @admin.display(description="Desa")
    def get_desa(self, obj):
        return obj.normalisasi.desa

    @admin.display(description="Tahap")
    def get_tahap(self, obj):
        return obj.normalisasi.tahap

    @admin.display(description="Tahun")
    def get_tahun(self, obj):
        return obj.normalisasi.tahun


# =========================================================
# PENGAJUAN BLT
# =========================================================

@admin.register(PengajuanBLT)
class PengajuanBLTAdmin(admin.ModelAdmin):
    list_display = (
        "desa",
        "noSK",
        "tahap",
        "tahun",
        "jumlah_kpm",
        "jumlah_dana",
        "status",
        "created_at",
    )

    search_fields = (
        "desa__nama_desa",
        "noSK",
    )

    list_filter = (
        "status",
        "tahun",
        "tahap",
        "desa",
    )

    readonly_fields = (
        "created_at",
        "tanggal_validasi",
    )

    fieldsets = (
        (
            "Data Pengajuan",
            {
                "fields": (
                    "desa",
                    "noSK",
                    "fileSK",
                    "file_hasil_saw",
                    "tahap",
                    "tahun",
                )
            },
        ),
        (
            "Informasi Dana",
            {
                "fields": (
                    "jumlah_dana",
                    "perbulan",
                    "jumlah_kpm",
                )
            },
        ),
        (
            "Validasi",
            {
                "fields": (
                    "status",
                    "catatan",
                    "divalidasi_oleh",
                    "tanggal_validasi",
                )
            },
        ),
        (
            "Informasi Sistem",
            {
                "fields": (
                    "created_at",
                )
            },
        ),
    )