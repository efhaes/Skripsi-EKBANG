from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from ekbang.proses.decorators import role_required
from ekbang.models import Desa, PengajuanBLT, HasilSAW
from django.utils import timezone
from ekbang.forms import DesaCreateForm
from django.contrib.auth.models import User
from ekbang.models import Profile


@login_required
@role_required('kecamatan')
def dashboard_kecamatan(request):
    context = {
        'total_desa': Desa.objects.count(),
        'total_pengajuan': PengajuanBLT.objects.count(),
        'pengajuan_pending': PengajuanBLT.objects.filter(status='pending').count(),
    }
    return render(request, 'kecamatan/dashboard.html', context)

@login_required
@role_required('kecamatan')
def desa_tambah(request):
    form = DesaCreateForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )

        
        Profile.objects.create(
            user=user,
            role='desa'
        )

        Desa.objects.create(
            user=user,
            dibuat_oleh=request.user,
            nama_desa=form.cleaned_data['nama_desa'],
            kecamatan=form.cleaned_data['kecamatan'],
            alamat_kantor=form.cleaned_data['alamat_kantor']
        )

        messages.success(request, 'Akun desa berhasil dibuat')
        return redirect('kecamatan_desa_list')

    return render(request, 'kecamatan/desa_form.html', {'form': form})

@login_required
@role_required('kecamatan')
def desa_edit(request, id):
    desa = get_object_or_404(Desa, id=id)
    user = desa.user

    if request.method == 'POST':
        form = DesaCreateForm(request.POST)
        form.user_instance = user  # ✅ BENAR

        if form.is_valid():
            user.username = form.cleaned_data['username']

            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)

            user.save()

            desa.nama_desa = form.cleaned_data['nama_desa']
            desa.kecamatan = form.cleaned_data['kecamatan']
            desa.alamat_kantor = form.cleaned_data['alamat_kantor']
            desa.save()

            messages.success(request, 'Data desa berhasil diperbarui')
            return redirect('kecamatan_desa_list')

    else:
        form = DesaCreateForm(initial={
            'username': user.username,
            'nama_desa': desa.nama_desa,
            'kecamatan': desa.kecamatan,
            'alamat_kantor': desa.alamat_kantor,
        })
        form.user_instance = user  # ✅ BENAR

    return render(request, 'kecamatan/desa_form.html', {
        'form': form,
        'edit': True
    })


@login_required
@role_required('kecamatan')
def desa_hapus(request, id):
    desa = get_object_or_404(Desa, id=id)

    if request.method == 'POST':
        user = desa.user
        desa.delete()
        user.delete()

        messages.success(request, 'Data desa berhasil dihapus')
        return redirect('kecamatan_desa_list')

    return render(request, 'kecamatan/desa_confirm_delete.html', {
        'desa': desa
    })



@login_required
@role_required('kecamatan')
def desa_list(request):
    desa = Desa.objects.select_related('user').all()
    return render(request, 'kecamatan/desa_list.html', {'desa': desa})


@login_required
@role_required('kecamatan')
def pengajuan_list(request):
    pengajuan = PengajuanBLT.objects.select_related('desa').order_by('-created_at')
    return render(request, 'kecamatan/pengajuan_list.html', {
        'pengajuan': pengajuan
    })




@login_required
@role_required('kecamatan')
def pengajuan_detail(request, pk):
    pengajuan = get_object_or_404(
        PengajuanBLT.objects.select_related('desa'),
        pk=pk
    )

    # ⛔ kalau sudah valid → tidak bisa divalidasi ulang
    if pengajuan.status == 'valid':
        messages.info(request, 'Pengajuan ini sudah divalidasi')
        return render(request, 'kecamatan/pengajuan_detail.html', {
            'pengajuan': pengajuan,
            'locked': True
        })

    if request.method == 'POST':
        status = request.POST.get('status')
        catatan = request.POST.get('catatan')

        if status in ['valid', 'tidak_valid']:
            pengajuan.status = status
            pengajuan.catatan = catatan

            # 🧾 LOG VALIDASI
            pengajuan.divalidasi_oleh = request.user
            pengajuan.tanggal_validasi = timezone.now()

            pengajuan.save()

            messages.success(request, 'Pengajuan berhasil divalidasi')
            return redirect('kecamatan_pengajuan_list')

    return render(request, 'kecamatan/pengajuan_detail.html', {
        'pengajuan': pengajuan,
        'locked': False
    })
