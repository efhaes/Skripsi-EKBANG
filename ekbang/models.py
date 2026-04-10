from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
import datetime

class Profile(models.Model):
    ROLE_CHOICES = (
        ('desa', 'Admin Desa'),
        ('kecamatan', 'Admin Kecamatan'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Desa(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='desa'
    )

    dibuat_oleh = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='desa_dibuat',
        help_text='Admin kecamatan yang membuat akun desa'
    )

    nama_desa = models.CharField(max_length=100)
    kecamatan = models.CharField(max_length=100)
    alamat_kantor = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama_desa

nik_validator = RegexValidator(
    regex=r'^\d{16}$',
    message='NIK harus terdiri dari 16 digit angka.'
)

kk_validator = RegexValidator(
    regex=r'^\d{16}$',
    message='No KK harus terdiri dari 16 digit angka.'
)

class Warga(models.Model):
    desa = models.ForeignKey(
        Desa,
        on_delete=models.CASCADE,
        related_name='warga'
    )

    nik = models.CharField(
        max_length=16,
        unique=True,
        validators=[nik_validator],
        verbose_name="NIK"
    )

    nama = models.CharField(max_length=100)
    jumlah_keluarga_kpm = models.IntegerField()
    alamat = models.TextField()

    # Kriteria SAW BLT
    desil_p3ke = models.IntegerField(
        help_text="Nilai 1–5 berdasarkan desil P3KE"
    )
    kehilangan_pekerjaan = models.IntegerField(
        help_text="1 = tidak, 5 = ya"
    )
    sakit_kronis = models.IntegerField(
        help_text="1 = tidak, 5 = ya"
    )
    tidak_pkh = models.IntegerField(
        help_text="1 = menerima PKH, 5 = tidak menerima"
    )
    lansia_tunggal = models.IntegerField(
        help_text="1 = tidak, 5 = ya"
    )
    perempuan_kepala = models.IntegerField(
        help_text="1 = tidak, 5 = ya"
    )
    def clean(self):
        try:
            tanggal = int(self.nik[6:8])
            bulan = int(self.nik[8:10])
            tahun = int(self.nik[10:12])

            # Jika perempuan → tanggal +40
            if tanggal > 40:
                tanggal -= 40

            # Tentukan abad
            tahun += 1900 if tahun > 30 else 2000

            datetime.date(tahun, bulan, tanggal)

        except Exception:
            raise ValidationError({
                'nik': 'Format tanggal lahir dalam NIK tidak valid.'
            })

    # 🔥 Supaya clean() selalu dijalankan
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nama} ({self.desa.nama_desa})"

    class Meta:
        indexes = [
            models.Index(fields=['nik']),

        ]

    def __str__(self):
        return f"{self.nama} ({self.desa.nama_desa})"
    



class HasilSAW(models.Model):
    desa = models.ForeignKey(
        Desa,
        on_delete=models.CASCADE,
        related_name='hasil_saw'
    )
    warga = models.ForeignKey(Warga, on_delete=models.CASCADE)
    nilai_preferensi = models.FloatField()
    ranking = models.IntegerField()
    tanggal_proses = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.warga.nama} - {self.desa.nama_desa} - Rank {self.ranking}"


class KuotaKPM(models.Model):
    desa = models.OneToOneField(Desa, on_delete=models.CASCADE, related_name='kuota_kpm')
    jumlah = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.desa} - {self.jumlah} KPM"


class PengajuanBLT(models.Model):
    desa = models.ForeignKey(
        Desa,
        on_delete=models.CASCADE,
        related_name='pengajuan'
    )
    noSK = models.CharField ()
    fileSK = models.FileField(upload_to='SK_BLT/')
    file_hasil_saw = models.FileField(upload_to='saw/')
    jumlah_dana = models.IntegerField()
    perbulan = models.IntegerField()
    jumlah_kpm = models.IntegerField()
    tahap = models.CharField(max_length=20)
    tahun = models.IntegerField()

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending','Pending'),
            ('valid','Valid'),
            ('tidak_valid','Tidak Valid')
        ],
        default='pending'
    )

    catatan = models.TextField(blank=True, null=True)

    # 🔥 LOG VALIDASI
    divalidasi_oleh = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pengajuan_divalidasi'
    )
    tanggal_validasi = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)



class NormalisasiSAW(models.Model):
    desa = models.ForeignKey(
        Desa,
        on_delete=models.CASCADE,
        related_name='normalisasi_saw'
    )
    warga = models.ForeignKey(
        Warga,
        on_delete=models.CASCADE
    )

    desil_p3ke = models.FloatField()
    kehilangan_pekerjaan = models.FloatField()
    sakit_kronis = models.FloatField()
    pkh = models.FloatField()
    lansia_tunggal = models.FloatField()
    perempuan_kepala = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
