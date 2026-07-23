from django.urls import path
from ekbang.views import desa as views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard_desa, name='desa_dashboard'),

    # Warga
    path('warga/', views.warga_list, name='desa_warga_list'),
    path('warga/tambah/', views.warga_tambah, name='desa_warga_tambah'),
    path('warga/<int:id>/detail/', views.warga_detail, name='desa_warga_detail'),
    path('warga/<int:id>/edit/', views.warga_edit, name='desa_warga_edit'),
    path('warga/<int:id>/hapus/', views.warga_hapus, name='desa_warga_hapus'),


    path('kriteria/', views.kriteria_list, name='desa_kriteria_list'),
    path('kriteria/tambah/', views.kriteria_tambah, name='desa_kriteria_tambah'),
    path('kriteria/<int:id>/edit/', views.kriteria_edit, name='desa_kriteria_edit'),
    path('kriteria/<int:id>/hapus/', views.kriteria_hapus, name='desa_kriteria_hapus'),

    path('subkriteria/', views.subkriteria_list, name='desa_subkriteria_list'),
    path('subkriteria/tambah/', views.subkriteria_tambah, name='desa_subkriteria_tambah'),
    path('subkriteria/<int:id>/edit/', views.subkriteria_edit, name='desa_subkriteria_edit'),
    path('subkriteria/<int:id>/hapus/', views.subkriteria_hapus, name='desa_subkriteria_hapus'),
    # SAW
    path('saw/proses/', views.proses_saw_view, name='desa_proses_saw'),
    path('saw/riwayat/', views.riwayat_saw_list, name='desa_riwayat_saw'),  # ← BARU (halaman list)
    path('saw/hasil/', views.hasil_saw_list, name='desa_perhitungan_saw'),         # ← halaman detail
    path('saw/hapus/', views.hapus_saw, name='desa_hapus_saw'),
    path('saw/kuota/', views.set_kuota_kpm, name='desa_set_kuota_kpm'),      # ← BARU
    path('saw/export-excel/', views.export_hasil_saw_excel, name='desa_export_saw_excel'),

    # Pengajuan BLT
    path('pengajuan/', views.pengajuan_blt, name='desa_pengajuan'),
    path('pengajuan/list/', views.pengajuan_blt_list, name='desa_pengajuan_list'),
    path('pengajuan/<int:id>/edit/', views.pengajuan_blt_edit, name='desa_pengajuan_edit'),
    path('pengajuan/<int:id>/hapus/', views.pengajuan_blt_hapus, name='desa_pengajuan_blt_hapus'),
    path('pengajuan/<int:id>/detail/', views.pengajuan_blt_detail, name='desa_pengajuan_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)