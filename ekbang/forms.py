from django import forms
from .models import Warga, PengajuanBLT, KuotaKPM, Kriteria, penilaianwarga,Kriteria, Subkriteria
from django.contrib.auth.models import User
from ekbang.models import Desa
from django.utils.text import slugify

class KriteriaForm(forms.ModelForm):
    class Meta:
        model = Kriteria
        fields = ['nama', 'kode', 'bobot', 'tipe', 'urutan', 'aktif']
        widgets = {
            'kode': forms.TextInput(attrs={'placeholder': 'Kosongkan untuk auto-generate dari nama'}),
        }

    def __init__(self, *args, desa=None, **kwargs):
        self.desa = desa
        super().__init__(*args, **kwargs)
        self.fields['kode'].required = False

    def clean_kode(self):
        kode = self.cleaned_data.get('kode', '').strip()
        nama = self.cleaned_data.get('nama') or self.data.get('nama', '')
        if not kode:
            kode = slugify(nama)
        if not kode:
            raise forms.ValidationError('Kode tidak boleh kosong.')

        qs = Kriteria.objects.filter(desa=self.desa, kode=kode)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Kode ini sudah dipakai kriteria lain di desa ini.')

        return kode

    def clean(self):
        cleaned = super().clean()
        bobot_baru = cleaned.get('bobot')
        aktif = cleaned.get('aktif')

        if bobot_baru is not None and aktif:
            qs = Kriteria.objects.filter(desa=self.desa, aktif=True)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            total_lain = sum(k.bobot for k in qs)
            total_baru = total_lain + bobot_baru

            if total_baru > 1:
                sisa = max(0, 1 - total_lain)
                self.add_error(
                    'bobot',
                    f'Total bobot kriteria aktif akan menjadi {total_baru:.2f}, melebihi batas maksimum 1.00. '
                    f'Sisa bobot yang tersedia: {sisa:.2f}.'
                )

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.desa = self.desa
        if commit:
            instance.save()
        return instance


class SubkriteriaForm(forms.ModelForm):
    class Meta:
        model = Subkriteria
        fields = ['kriteria', 'label', 'nilai', 'urutan']

    def __init__(self, *args, desa=None, **kwargs):
        self.desa = desa
        super().__init__(*args, **kwargs)
        self.fields['kriteria'].queryset = Kriteria.objects.filter(desa=desa).order_by('urutan', 'nama')
        self.fields['kriteria'].empty_label = "-- Pilih Kriteria --"

    def clean(self):
        cleaned = super().clean()
        kriteria = cleaned.get('kriteria')
        label = cleaned.get('label')

        if kriteria and label:
            qs = Subkriteria.objects.filter(kriteria=kriteria, label=label.strip())
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('label', 'Label ini sudah dipakai di kriteria yang sama.')

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance

class WargaForm(forms.ModelForm):
    """
    Form warga sekarang dinamis: field penilaian dibuat on-the-fly
    berdasarkan Kriteria yang aktif milik desa terkait, bukan hardcoded.

    WAJIB kasih parameter `desa` saat instantiate form ini, contoh:
        WargaForm(request.POST or None, desa=desa)
        WargaForm(request.POST or None, instance=warga, desa=desa)
    """

    def __init__(self, *args, desa=None, **kwargs):
        instance = kwargs.get('instance')
        # Kalau desa tidak dikasih eksplisit tapi ada instance, ambil dari situ
        self.desa = desa or (instance.desa if instance else None)

        super().__init__(*args, **kwargs)

        if self.desa is None:
            raise ValueError("WargaForm butuh parameter 'desa' atau 'instance' yang sudah punya desa.")

        self.kriteria_list = list(
            Kriteria.objects.filter(desa=self.desa, aktif=True).prefetch_related('subkriteria')
        )

        # Kalau lagi edit, ambil nilai yang sudah tersimpan supaya radio ke-select otomatis
        nilai_tersimpan = {}
        if instance and instance.pk:
            nilai_tersimpan = {
                nk.kriteria_id: nk.subkriteria_id
                for nk in instance.nilai_kriteria.all()
            }

        # Bikin field dinamis: satu ChoiceField per Kriteria
        for kriteria in self.kriteria_list:
            field_name = f'kriteria_{kriteria.id}'
            choices = [(sub.id, sub.label) for sub in kriteria.subkriteria.all()]
            self.fields[field_name] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect,
                label=kriteria.nama,
                required=True,
                initial=nilai_tersimpan.get(kriteria.id),
            )

    def clean_nik(self):
        nik = self.cleaned_data.get('nik')
        if nik and not nik.isdigit():
            raise forms.ValidationError("NIK hanya boleh berisi angka (0-9).")
        return nik

    def save_nilai_kriteria(self, warga):
        """
        Panggil manual di view SETELAH warga.save() dipanggil,
        karena WargaNilaiKriteria butuh warga.pk yang sudah ada.
        """
        for kriteria in self.kriteria_list:
            field_name = f'kriteria_{kriteria.id}'
            subkriteria_id = self.cleaned_data.get(field_name)
            if subkriteria_id:
                penilaianwarga.objects.update_or_create(
                    warga=warga,
                    kriteria=kriteria,
                    defaults={'subkriteria_id': subkriteria_id}
                )

    class Meta:
        model = Warga
        fields = [
            'nik',
            'no_kk',
            'nama',
            'jumlah_keluarga_kpm',
            'alamat',
        ]
        labels = {
            'nik': 'NIK',
            'no_kk': 'No. KK',
            'nama': 'Nama Lengkap',
            'jumlah_keluarga_kpm': 'Jumlah Anggota Keluarga',
            'alamat': 'Alamat',
        }
        error_messages = {
            'nik': {
                'required': 'NIK wajib diisi.',
                'unique': 'NIK sudah terdaftar di sistem.',
                'max_length': 'NIK harus terdiri dari 16 digit.',
                'min_length': 'NIK harus terdiri dari 16 digit.',
            },
            'no_kk': {
                'required': 'No. KK wajib diisi.',
                'max_length': 'No. KK harus terdiri dari 16 digit.',
                'min_length': 'No. KK harus terdiri dari 16 digit.',
            }
        }
        widgets = {
            'alamat': forms.Textarea(attrs={'rows': 3}),
        }


class PengajuanBLTForm(forms.ModelForm):
    def clean_fileSK(self):
        file = self.cleaned_data.get('fileSK')
        if file:
            allowed_extensions = ['.doc', '.docx', '.xls', '.xlsx', '.pdf']
            ext = file.name.lower().split('.')[-1]
            if f'.{ext}' not in allowed_extensions:
                raise forms.ValidationError('File SK harus berupa Word (.doc, .docx), Excel (.xls, .xlsx), atau PDF (.pdf)')
        return file

    def clean_file_hasil_saw(self):
        file = self.cleaned_data.get('file_hasil_saw')
        if file:
            allowed_extensions = ['.doc', '.docx', '.xls', '.xlsx', '.pdf']
            ext = file.name.lower().split('.')[-1]
            if f'.{ext}' not in allowed_extensions:
                raise forms.ValidationError('File hasil SAW harus berupa Word (.doc, .docx), Excel (.xls, .xlsx), atau PDF (.pdf)')
        return file

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
    username = forms.CharField(max_length=150, label='Username Akun Desa')
    password = forms.CharField(widget=forms.PasswordInput, label='Password', required=False)
    nama_desa = forms.CharField(max_length=100, label='Nama Desa')
    kecamatan = forms.CharField(max_length=100, label='Kecamatan')
    alamat_kantor = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label='Alamat Kantor Desa')

    def __init__(self, *args, **kwargs):
        self.user_instance = None
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username']

        if self.user_instance:
            if User.objects.filter(username=username).exclude(id=self.user_instance.id).exists():
                raise forms.ValidationError('Username sudah digunakan')
        else:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError('Username sudah digunakan')

        return username


class KuotaKPMForm(forms.ModelForm):
    class Meta:
        model = KuotaKPM
        fields = ['tahap', 'tahun', 'jumlah']
        labels = {
            'tahap': 'Tahap',
            'tahun': 'Tahun',
            'jumlah': 'Jumlah Penerima BLT (KPM)'
        }
        widgets = {
            'tahap': forms.Select(choices=[
                ('1', 'Tahap 1'),
                ('2', 'Tahap 2'),
                ('3', 'Tahap 3'),
            ]),
            'tahun': forms.NumberInput(attrs={
                'min': 2020,
                'max': 2099,
                'placeholder': 'Contoh: 2025'
            }),
            'jumlah': forms.NumberInput(attrs={
                'min': 1,
                'placeholder': 'Masukkan jumlah KPM'
            })
        }