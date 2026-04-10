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
    path('warga/<int:id>/edit/', views.warga_edit, name='desa_warga_edit'),
    path('warga/<int:id>/hapus/', views.warga_hapus, name='desa_warga_hapus'),

    # SAW
    # urls.py — tidak perlu diubah, path() Django otomatis terima GET dan POST
    path('saw/proses/', views.proses_saw_view, name='desa_proses_saw'),
    path('saw/hasil/', views.hasil_saw_list, name='desa_hasil_saw'),
    path(
        'saw/export-excel/',
        views.export_hasil_saw_excel,
        name='desa_export_saw_excel'
    ),

    # Pengajuan BLT
    path('pengajuan/', views.pengajuan_blt, name='desa_pengajuan'),
    path('pengajuan/list/', views.pengajuan_blt_list, name='desa_pengajuan_list'),
    path('pengajuan/<int:id>/edit/', views.pengajuan_blt_edit, name='desa_pengajuan_edit'),
    path('pengajuan/<int:id>/hapus/', views.pengajuan_blt_hapus, name='desa_pengajuan_blt_hapus'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)