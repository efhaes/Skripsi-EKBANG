from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ekbang.proses.decorators import role_required

from ekbang.models import Desa, Warga, HasilSAW, PengajuanBLT,NormalisasiSAW
from ekbang.proses.saw import hitung_saw
from ekbang.forms import WargaForm, PengajuanBLTForm
from django.http import HttpResponse
from openpyxl import Workbook
@login_required
@role_required('desa')
def dashboard_desa(request):
    desa = request.user.desa

    context = {
        'total_warga': Warga.objects.filter(desa=desa).count(),
        'total_hasil': HasilSAW.objects.filter(desa=desa).count(),
        'pengajuan': PengajuanBLT.objects.filter(desa=desa).order_by('-created_at')[:5],
        'total_pengajuan': PengajuanBLT.objects.filter(desa=desa).count(),
        'pengajuan_pending': PengajuanBLT.objects.filter(
            desa=desa,
            status='pending'
        ).count(),
        }
    return render(request, 'desa/dashboard.html', context)

@login_required
@role_required('desa')
def warga_list(request):
    desa = request.user.desa
    warga = Warga.objects.filter(desa=desa)
    return render(request, 'desa/warga_list.html', {'warga': warga})

@login_required
@role_required('desa')
def warga_tambah(request):
    desa = request.user.desa
    form = WargaForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        warga = form.save(commit=False)
        warga.desa = desa
        warga.save()
        messages.success(request, 'Data warga berhasil ditambahkan')
        return redirect('desa_warga_list')

    return render(request, 'desa/warga_form.html', {'form': form})


@login_required
@role_required('desa')
def warga_edit(request, id):
    desa = request.user.desa
    warga = get_object_or_404(Warga, id=id, desa=desa)
    form = WargaForm(request.POST or None, instance=warga)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Data warga berhasil diupdate')
        return redirect('desa_warga_list')

    return render(request, 'desa/warga_form.html', {'form': form})


@login_required
@role_required('desa')
def warga_hapus(request, id):
    desa = request.user.desa
    warga = get_object_or_404(Warga, id=id, desa=desa)
    warga.delete()
    messages.success(request, 'Data warga dihapus')
    return redirect('desa_warga_list')

@login_required
@role_required('desa')
def proses_saw_view(request):
    desa = request.user.desa

    warga_ada = Warga.objects.filter(desa=desa).exists()
    if not warga_ada:
        messages.warning(request, 'Data warga masih kosong')
        return redirect('desa_hasil_saw')

    hitung_saw(desa)  # 🔥 NGITUNG CUMA DI SINI

    messages.success(request, 'Proses SAW berhasil dijalankan')
    return redirect('desa_hasil_saw')



@login_required
@role_required('desa')
def hasil_saw_list(request):
    desa = request.user.desa
    normalisasi = NormalisasiSAW.objects.filter(
    desa=desa
    ).select_related('warga')

    hasil = HasilSAW.objects.filter(
        desa=desa
    ).select_related('warga').order_by('ranking')

    return render(request, 'desa/hasil_saw.html', {
    'hasil': hasil,
    'normalisasi': normalisasi,
    'sudah_diproses': hasil.exists()
})





@login_required
@role_required('desa')
def pengajuan_blt(request):
    desa = request.user.desa
    form = PengajuanBLTForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        pengajuan = form.save(commit=False)
        pengajuan.desa = desa
        pengajuan.save()
        messages.success(request, 'Pengajuan BLT berhasil dikirim')
        return redirect('desa_dashboard')

    return render(request, 'desa/pengajuan_form.html', {'form': form})

@login_required
@role_required('desa')
def pengajuan_blt_list(request):
    desa = request.user.desa
    pengajuan = PengajuanBLT.objects.filter(desa=desa).order_by('-created_at')
    return render(request, 'desa/pengajuan_blt_list.html', {'pengajuan': pengajuan})


@login_required
@role_required('desa')
def pengajuan_blt_hapus(request, id):
    desa = request.user.desa
    pengajuan = get_object_or_404(PengajuanBLT, id=id, desa=desa)
    pengajuan.delete()
    messages.success(request, 'Data pengajuan BLT dihapus')
    return redirect('desa_pengajuan_list')

@login_required
@role_required('desa')
def pengajuan_blt_edit(request, id):
    desa = request.user.desa
    pengajuan = get_object_or_404(PengajuanBLT, id=id, desa=desa)

    form = PengajuanBLTForm(request.POST or None, request.FILES or None, instance=pengajuan)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Pengajuan BLT berhasil diperbarui')
        return redirect('desa_pengajuan_list')

    return render(request, 'desa/pengajuan_form.html', {'form': form})


from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect

@login_required
@role_required('desa')
def export_hasil_saw_excel(request):
    desa = request.user.desa

    hasil = HasilSAW.objects.filter(desa=desa).order_by('ranking')
    normalisasi = NormalisasiSAW.objects.filter(desa=desa)

    if not hasil.exists():
        messages.warning(request, 'Belum ada hasil SAW')
        return redirect('desa_hasil_saw')

    wb = Workbook()

    # =========================
    # 📊 SHEET 1: HASIL SAW
    # =========================
    ws = wb.active
    ws.title = "Hasil SAW"

    headers = [
        'Ranking',
        'NIK',
        'Nama Warga',
        'Alamat',

        # 🔹 Normalisasi
        'N Desil P3KE',
        'N Kehilangan Pekerjaan',
        'N Sakit Kronis',
        'N Tidak PKH',
        'N Lansia Tunggal',
        'N Perempuan Kepala',

        # 🔹 Hasil akhir
        'Nilai Preferensi',
        'Desa',
        'Tanggal Proses'
    ]

    ws.append(headers)

    for cell in ws[1]:
        cell.font = Font(bold=True)

    from django.shortcuts import get_object_or_404

    for h in hasil:
        n = NormalisasiSAW.objects.filter(
            desa=desa,
            warga=h.warga
         ).first()


        ws.append([
        h.ranking,
        h.warga.nik,
        h.warga.nama,
        h.warga.alamat,

        round(n.desil_p3ke, 4) if n else 0,
        round(n.kehilangan_pekerjaan, 4) if n else 0,
        round(n.sakit_kronis, 4) if n else 0,
        round(n.pkh, 4) if n else 0,
        round(n.lansia_tunggal, 4) if n else 0,
        round(n.perempuan_kepala, 4) if n else 0,

        round(h.nilai_preferensi, 4),
        desa.nama_desa,
        h.tanggal_proses.strftime('%d-%m-%Y %H:%M')
        if h.tanggal_proses else '-'
    ])


    # auto width
    for col in ws.columns:
        length = max(len(str(cell.value)) if cell.value else 0 for cell in col)
        ws.column_dimensions[get_column_letter(col[0].column)].width = length + 3

    # =========================
    # 📐 SHEET 2: NORMALISASI
    # =========================
    ws2 = wb.create_sheet(title="Normalisasi SAW")

    headers_norm = [
    'NIK', 'Nama Warga',
    'Desil P3KE',
    'Kehilangan Pekerjaan',
    'Sakit Kronis',
    'PKH',
    'Lansia Tunggal',
    'Perempuan Kepala',
    'Tanggal Proses'
    ]

    ws2.append(headers_norm)

    for cell in ws2[1]:
        cell.font = Font(bold=True)

    for n in normalisasi:
        ws2.append([
        n.warga.nik,
        n.warga.nama,
        round(n.desil_p3ke, 4),
        round(n.kehilangan_pekerjaan, 4),
        round(n.sakit_kronis, 4),
        round(n.pkh, 4),
        round(n.lansia_tunggal, 4),
        round(n.perempuan_kepala, 4),
        n.created_at.strftime('%d-%m-%Y %H:%M')
        ])


    for col in ws2.columns:
        length = max(len(str(cell.value)) if cell.value else 0 for cell in col)
        ws2.column_dimensions[get_column_letter(col[0].column)].width = length + 3

    # =========================
    # 📤 RESPONSE
    # =========================
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"Hasil_SAW_BLT_{desa.nama_desa}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    wb.save(response)
    return response
