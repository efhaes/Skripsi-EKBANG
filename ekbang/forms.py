from django import forms
from .models import Warga, PengajuanBLT
from django import forms
from django.contrib.auth.models import User
from ekbang.models import Desa

NILAI_KRITERIA = [
    (1, 'Tidak Memenuhi'),
    (3, 'Memenuhi Sebagian'),
    (5, 'Memenuhi Penuh'),
]

class WargaForm(forms.ModelForm):
    class Meta:
        model = Warga
        fields = [
            'nik',
            'nama',
            'jumlah_keluarga_kpm',
            'alamat',
            'desil_p3ke',
            'kehilangan_pekerjaan',
            'sakit_kronis',
            'tidak_pkh',
            'lansia_tunggal',
            'perempuan_kepala',
        ]
        widgets = {
            'alamat': forms.Textarea(attrs={'rows': 3}),

            'desil_p3ke': forms.RadioSelect(choices=[
                (1, 'Desil 1 – Sangat Miskin (Prioritas Utama)'),
                (2, 'Desil 2 – Miskin'),
                (3, 'Desil 3 – Rentan Miskin'),
                (4, 'Desil 4 – Hampir Rentan'),
            ]),

            'kehilangan_pekerjaan': forms.RadioSelect(choices=[
                (1, 'Tidak kehilangan pekerjaan'),
                (3, 'Kehilangan sementara'),
                (5, 'Kehilangan tetap')
            ]),

            'sakit_kronis': forms.RadioSelect(choices=[
                (1, 'Tidak ada'),
                (3, 'Sakit kronis ringan'),
                (5, 'Sakit kronis berat / difabel')
            ]),

            'tidak_pkh': forms.RadioSelect(choices=[
                (1, 'Menerima PKH'),
                (5, 'Tidak menerima PKH')
            ]),

            'lansia_tunggal': forms.RadioSelect(choices=[
                (1, 'Bukan lansia tunggal'),
                (5, 'Lansia tunggal')
            ]),

            'perempuan_kepala': forms.RadioSelect(choices=[
                (1, 'Bukan'),
                (5, 'Perempuan kepala keluarga')
            ]),
        }
def clean_nik(self):
    nik = self.cleaned_data.get('nik')

    if nik and not nik.isdigit():
        raise forms.ValidationError("NIK hanya boleh berisi angka (0-9).")

    return nik

class Meta:
    model = Warga
    fields = [...]
    labels = {
        'nik': 'NIK'
    }
    error_messages = {
        'nik': {
            'required': 'NIK wajib diisi.',
            'unique': 'NIK sudah terdaftar di sistem.',
            'invalid': 'NIK harus terdiri dari 16 digit angka.',
            'max_length': 'NIK harus terdiri dari 16 digit.',
            'min_length': 'NIK harus terdiri dari 16 digit.',
        }
    }



class PengajuanBLTForm(forms.ModelForm):
    class Meta:
        model = PengajuanBLT
        fields = [
            'noSK',
            'fileSK',
            'file_hasil_saw',
            'jumlah_dana',
            'perbulan',
            'jumlah_kpm',
            'tahap',
            'tahun',
        ]


class DesaCreateForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label='Username Akun Desa'
    )

    password = forms.CharField(
        widget=forms.PasswordInput,
        label='Password',
        required=False
    )

    nama_desa = forms.CharField(
        max_length=100,
        label='Nama Desa'
    )

    kecamatan = forms.CharField(
        max_length=100,
        label='Kecamatan'
    )

    alamat_kantor = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Alamat Kantor Desa'
    )

    def __init__(self, *args, **kwargs):
        self.user_instance = None  # 🔥 DEFAULT AMAN
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username']

        if self.user_instance:
            if User.objects.filter(username=username).exclude(
                id=self.user_instance.id
            ).exists():
                raise forms.ValidationError('Username sudah digunakan')
        else:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError('Username sudah digunakan')

        return username
