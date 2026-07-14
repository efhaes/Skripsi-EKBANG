from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import datetime

class AdminKecamatan(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_kecamatan')
    nama_kecamatan = models.CharField(max_length=100)
    alamat_kantor = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Admin Kecamatan – {self.nama_kecamatan}"

    class Meta:
        verbose_name = "Admin Kecamatan"
        verbose_name_plural = "Admin Kecamatan"


class Desa(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='desa')
    dibuat_oleh = models.ForeignKey(
        AdminKecamatan, on_delete=models.CASCADE, related_name='desa_dibuat',
        help_text='Admin kecamatan yang membuat akun desa'
    )
    nama_desa = models.CharField(max_length=100)
    kecamatan = models.CharField(max_length=100)
    alamat_kantor = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama_desa


nik_validator = RegexValidator(regex=r'^\d{16}$', message='NIK harus terdiri dari 16 digit angka.')
kk_validator = RegexValidator(regex=r'^\d{16}$', message='No KK harus terdiri dari 16 digit angka.')


# =========================================================
# BARU: KRITERIA & SUBKRITERIA DINAMIS
# =========================================================

class Kriteria(models.Model):
    TIPE_CHOICES = [('benefit', 'Benefit'), ('cost', 'Cost')]
    desa = models.ForeignKey(Desa, on_delete=models.CASCADE, related_name='kriteria')
    kode = models.SlugField(max_length=50)
    nama = models.CharField(max_length=100)
    bobot = models.FloatField(default=0)
    tipe = models.CharField(max_length=10, choices=TIPE_CHOICES, default='benefit')
    urutan = models.IntegerField(default=0)
    aktif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('desa', 'kode')
        ordering = ['urutan', 'id']

    def __str__(self):
        return f"{self.nama} - {self.desa.nama_desa}"


class Subkriteria(models.Model):
    kriteria = models.ForeignKey(Kriteria, on_delete=models.CASCADE, related_name='subkriteria')
    label = models.CharField(max_length=100)
    nilai = models.FloatField()
    urutan = models.IntegerField(default=0)

    class Meta:
        unique_together = ('kriteria', 'label')
        ordering = ['urutan', 'id']

    def __str__(self):
        return f"{self.label} ({self.kriteria.nama})"


# =========================================================
# WARGA (field lama masih ada — JANGAN dihapus dulu di tahap ini)
# =========================================================

class Warga(models.Model):
    desa = models.ForeignKey(Desa, on_delete=models.CASCADE, related_name='warga')
    no_kk = models.CharField(max_length=16, blank=True, null=True)
    nik = models.CharField(max_length=16, unique=True, validators=[nik_validator], verbose_name="NIK")
    nama = models.CharField(max_length=100)
    jumlah_keluarga_kpm = models.IntegerField()
    alamat = models.TextField()
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    def clean(self):
        try:
            tanggal = int(self.nik[6:8])
            bulan = int(self.nik[8:10])
            tahun = int(self.nik[10:12])
            if tanggal > 40:
                tanggal -= 40
            tahun += 1900 if tahun > 30 else 2000
            datetime.date(tahun, bulan, tanggal)
        except Exception:
            raise ValidationError({'nik': 'Format tanggal lahir dalam NIK tidak valid.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nama} ({self.desa.nama_desa})"

    class Meta:
        indexes = [models.Index(fields=['nik'])]


class penilaianwarga(models.Model):
    warga = models.ForeignKey(Warga, on_delete=models.CASCADE, related_name='nilai_kriteria')
    kriteria = models.ForeignKey(Kriteria, on_delete=models.CASCADE, related_name='nilai_warga')
    subkriteria = models.ForeignKey(Subkriteria, on_delete=models.PROTECT, related_name='nilai_warga')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('warga', 'kriteria')

    def clean(self):
        if self.subkriteria_id and self.kriteria_id:
            if self.subkriteria.kriteria_id != self.kriteria_id:
                raise ValidationError({'subkriteria': 'Subkriteria tidak sesuai dengan kriteria yang dipilih.'})
        if self.warga_id and self.kriteria_id:
            if self.kriteria.desa_id != self.warga.desa_id:
                raise ValidationError({'kriteria': 'Kriteria tidak sesuai dengan desa warga ini.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.warga.nama} - {self.kriteria.nama}: {self.subkriteria.label}"


# =========================================================
# KUOTA KPM
# =========================================================

class KuotaKPM(models.Model):
    desa = models.ForeignKey(Desa, on_delete=models.CASCADE, related_name='kuota_kpm')
    tahap = models.CharField(max_length=20)
    tahun = models.IntegerField()
    jumlah = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('desa', 'tahap', 'tahun')

    def __str__(self):
        return f"{self.desa} - Tahap {self.tahap} {self.tahun} - {self.jumlah} KPM"


# =========================================================
# NORMALISASI SAW (field lama masih ada)
# =========================================================

class NormalisasiSAW(models.Model):
    desa = models.ForeignKey(Desa, on_delete=models.CASCADE, related_name='normalisasi_saw')
    warga = models.ForeignKey(Warga, on_delete=models.SET_NULL, null=True, blank=True)
    nama_warga_arsip = models.CharField(max_length=100, blank=True, null=True)
    tahap = models.CharField(max_length=20)
    tahun = models.IntegerField()
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('desa', 'warga', 'tahap', 'tahun')

    def __str__(self):
        nama = self.nama_warga_arsip or (self.warga.nama if self.warga else 'Warga Terhapus')
        return f"{nama} - Normalisasi Tahap {self.tahap} {self.tahun}"


class NormalisasiSAWDetail(models.Model):
    normalisasi = models.ForeignKey(NormalisasiSAW, on_delete=models.CASCADE, related_name='detail')
    kriteria = models.ForeignKey(Kriteria, on_delete=models.CASCADE, related_name='detail_normalisasi')
    nilai_normalisasi = models.FloatField()

    class Meta:
        unique_together = ('normalisasi', 'kriteria')

    def __str__(self):
        return f"{self.normalisasi} - {self.kriteria.nama}: {self.nilai_normalisasi}"

# =========================================================
# HASIL SAW (tidak ada field lama yang perlu dipindah)
# =========================================================

class HasilSAW(models.Model):
    normalisasi = models.ForeignKey(NormalisasiSAW,on_delete=models.CASCADE,related_name='hasil')
    nilai_preferensi = models.FloatField()
    ranking = models.IntegerField()
    tanggal_proses = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.normalisasi} - Rank {self.ranking}"


# =========================================================
# PENGAJUAN BLT
# =========================================================

class PengajuanBLT(models.Model):
    desa = models.ForeignKey(Desa, on_delete=models.CASCADE, related_name='pengajuan')
    divalidasi_oleh = models.ForeignKey(
        AdminKecamatan, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='pengajuan_divalidasi'
    )
    noSK = models.CharField(max_length=70)
    fileSK = models.FileField(
        upload_to='SK_BLT/',
        validators=[FileExtensionValidator(['doc', 'docx', 'xls', 'xlsx', 'pdf'])]
    )
    file_hasil_saw = models.FileField(
        upload_to='saw/',
        validators=[FileExtensionValidator(['doc', 'docx', 'xls', 'xlsx', 'pdf'])]
    )
    jumlah_dana = models.IntegerField()
    perbulan = models.IntegerField()
    jumlah_kpm = models.IntegerField()
    tahap = models.CharField(max_length=20)
    tahun = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('valid', 'Valid'), ('tidak_valid', 'Tidak Valid')],
        default='pending'
    )
    catatan = models.TextField(blank=True, null=True)
    tanggal_validasi = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)