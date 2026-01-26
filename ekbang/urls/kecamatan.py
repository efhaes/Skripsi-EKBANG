from django.urls import path
from ekbang.views import kecamatan as views

urlpatterns = [
    path('dashboard/', views.dashboard_kecamatan, name='kecamatan_dashboard'),

    path('desa/', views.desa_list, name='kecamatan_desa_list'),
    path('desa/tambah/', views.desa_tambah, name='kecamatan_desa_tambah'),
    path('desa/<int:id>/edit/', views.desa_edit, name='kecamatan_desa_edit'),
    path('desa/<int:id>/hapus/', views.desa_hapus, name='kecamatan_desa_hapus'),


    path('pengajuan/', views.pengajuan_list, name='kecamatan_pengajuan_list'),
    path(
    'kecamatan/pengajuan/<int:pk>/validasi/',
    views.pengajuan_detail,
    name='kecamatan_pengajuan_detail'
)
]
