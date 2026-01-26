from django.contrib.auth.models import User
from django.db import models

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


class Warga(models.Model):
    desa = models.ForeignKey(
        Desa,
        on_delete=models.CASCADE,
        related_name='warga'
    )

    nik = models.CharField(max_length=20, unique=True)
    nama = models.CharField(max_length=100)
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



from django.contrib.auth.models import User

class PengajuanBLT(models.Model):
    desa = models.ForeignKey(
        Desa,
        on_delete=models.CASCADE,
        related_name='pengajuan'
    )
    file_hasil_saw = models.FileField(upload_to='saw/')
    jumlah_dana = models.IntegerField()
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
